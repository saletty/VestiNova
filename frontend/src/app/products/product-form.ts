import { Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { AbstractControl, FormControl, FormGroup, ReactiveFormsModule, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { productError } from './product-errors';
import { Product, ProductInput } from './product.model';
import { ProductService } from './product.service';

function productName(control: AbstractControl): ValidationErrors | null {
  return String(control.value ?? '').trim().length >= 3 ? null : { nameLength: true };
}

export function productPrice(control: AbstractControl): ValidationErrors | null {
  const price = String(control.value ?? '').trim();
  return /^\d{1,8}(?:[.,]\d{1,2})?$/.test(price) && /[1-9]/.test(price)
    ? null : { productPrice: true };
}

function productSlug(control: AbstractControl): ValidationErrors | null {
  const slug = String(control.value ?? '').trim();
  return slug === '' || (slug.length >= 3 && slug.length <= 140 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug))
    ? null : { productSlug: true };
}

function imageUrl(control: AbstractControl): ValidationErrors | null {
  const value = String(control.value ?? '').trim();
  if (!value) return null;
  try {
    const url = new URL(value);
    return ['http:', 'https:'].includes(url.protocol) && Boolean(url.hostname) && !url.username && !url.password ? null : { imageUrl: true };
  } catch { return { imageUrl: true }; }
}

/** Normaliza el separador y los centavos sin convertir el importe a float. */
export function decimalPrice(value: string): string {
  const [integer, fraction = ''] = value.trim().replace(',', '.').split('.');
  return `${integer.replace(/^0+(?=\d)/, '')}.${fraction.padEnd(2, '0')}`;
}

@Component({
  selector: 'app-product-form',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './product-form.html',
  styleUrl: './products.css',
})
export class ProductFormPage {
  private readonly products = inject(ProductService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly rawId = this.route.snapshot.paramMap.get('id');
  readonly editing = this.rawId !== null;
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly loadError = signal<string | null>(null);
  readonly error = signal<string | null>(null);
  readonly original = signal<Product | null>(null);
  readonly form = new FormGroup({
    nombre: new FormControl('', { nonNullable: true, validators: [Validators.required, productName, Validators.maxLength(120)] }),
    descripcion: new FormControl('', { nonNullable: true, validators: [Validators.maxLength(3000)] }),
    precio: new FormControl('', { nonNullable: true, validators: [Validators.required, productPrice] }),
    slug: new FormControl('', { nonNullable: true, validators: [productSlug] }),
    imagen_url: new FormControl('', { nonNullable: true, validators: [imageUrl, Validators.maxLength(2048)] }),
    activo: new FormControl(true, { nonNullable: true }),
  });

  ngOnInit(): void {
    this.products.notice.set(null);
    if (this.editing) {
      this.form.controls.slug.addValidators(Validators.required);
      this.load();
    }
  }

  load(): void {
    const id = Number(this.rawId);
    if (!/^[1-9]\d*$/.test(this.rawId ?? '') || !Number.isSafeInteger(id)) { this.loadError.set('La dirección del producto no es válida.'); return; }
    this.loading.set(true);
    this.loadError.set(null);
    this.products.get(id).pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: product => {
        this.original.set(product);
        this.form.setValue({
          nombre: product.nombre, descripcion: product.descripcion, precio: product.precio,
          slug: product.slug, imagen_url: product.imagen_url ?? '', activo: product.activo,
        });
        this.form.markAsPristine();
        this.loading.set(false);
      },
      error: error => { this.loading.set(false); this.loadError.set(productError(error)); },
    });
  }

  fieldError(name: keyof typeof this.form.controls): string | null {
    const control = this.form.controls[name];
    if (!control.touched || !control.errors) return null;
    if (control.hasError('required')) return 'Este campo es obligatorio.';
    if (control.hasError('nameLength')) return 'Escribe al menos 3 caracteres.';
    if (control.hasError('maxlength')) return `El límite es ${control.errors['maxlength'].requiredLength} caracteres.`;
    if (control.hasError('productPrice')) return 'Usa un precio mayor a 0, hasta 99999999.99, con dos decimales como máximo.';
    if (control.hasError('productSlug')) return 'Usa de 3 a 140 letras minúsculas, números y guiones entre palabras.';
    if (control.hasError('imageUrl')) return 'Introduce una URL http o https completa y sin credenciales.';
    return 'Revisa este campo.';
  }

  submit(): void {
    if (this.saving() || this.loading() || this.loadError()) return;
    this.error.set(null);
    if (this.form.invalid) { this.form.markAllAsTouched(); this.error.set('Revisa los campos indicados antes de guardar.'); return; }
    const value = this.form.getRawValue();
    const input: ProductInput = {
      nombre: value.nombre.trim(), descripcion: value.descripcion.trim(),
      precio: decimalPrice(value.precio), imagen_url: value.imagen_url.trim() || null,
      activo: value.activo,
      ...(value.slug.trim() ? { slug: value.slug.trim() } : {}),
    };
    const original = this.original();
    if (this.editing && original === null) return;
    const changes: Partial<ProductInput> = {};
    if (original !== null) {
      for (const key of Object.keys(input) as (keyof ProductInput)[]) {
        if (input[key] !== original[key]) Object.assign(changes, { [key]: input[key] });
      }
      if (Object.keys(changes).length === 0) { this.error.set('No hay cambios para guardar.'); return; }
    }
    this.saving.set(true);
    const request = original !== null ? this.products.update(original.id, changes) : this.products.create(input);
    request.pipe(takeUntilDestroyed(this.destroyRef)).subscribe({
      next: () => {
        this.products.notice.set(this.editing ? 'Cambios guardados en el producto.' : 'Producto registrado correctamente.');
        void this.router.navigate(['/admin/productos']).then(navigated => {
          if (!navigated) { this.saving.set(false); this.error.set('El producto se guardó. Vuelve al listado para consultarlo.'); }
        });
      },
      error: error => { this.saving.set(false); this.error.set(productError(error)); },
    });
  }
}
