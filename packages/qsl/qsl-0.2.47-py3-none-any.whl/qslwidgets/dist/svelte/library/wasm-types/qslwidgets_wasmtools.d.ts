/* tslint:disable */
/* eslint-disable */
export function main_js(): void;
export class Dimensions {
  private constructor();
  free(): void;
  width: number;
  height: number;
}
export class HSV {
  private constructor();
  free(): void;
  h: number;
  s: number;
  v: number;
}
export class Image {
  free(): void;
  constructor(raw: Uint8ClampedArray | null | undefined, width: number, height: number);
}
export class Mask {
  free(): void;
  constructor(values: Uint8ClampedArray | null | undefined, width: number, height: number);
  static from_flood(image: Image, x: number, y: number, dx: number, dy: number, threshold: number, limit: number): Mask;
  fill_inplace(x: number, y: number, width: number, height: number, value: number): void;
  fill(x: number, y: number, dx: number, dy: number, value: number): Mask;
  dimensions(): any;
  contents(): Uint8Array;
  get(x: number, y: number): number;
  flood(image: Image, x: number, y: number, dx: number, dy: number, threshold: number, limit: number): Mask;
}