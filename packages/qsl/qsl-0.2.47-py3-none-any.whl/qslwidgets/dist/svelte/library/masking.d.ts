import type { ImageData, Point, Dimensions, Bitmap, RLEMap, MaskLabel, StackContentLayer } from "./types";
import { Image, Mask } from "../../wasmtools/Cargo.toml";
declare const img2hsv: (img: HTMLImageElement | HTMLVideoElement, canvas: HTMLCanvasElement, maxSize: number, transform?: {
    size: Dimensions;
    layer: StackContentLayer;
}) => ImageData;
declare const rle2bmp: (rlemap: RLEMap) => Bitmap;
declare const bmp2rle: (bitmap: Bitmap) => RLEMap;
declare const findMaskByPoint: (point: Point, masks: MaskLabel<Bitmap>[]) => number;
export { Image, Mask, img2hsv, findMaskByPoint, bmp2rle, rle2bmp };
