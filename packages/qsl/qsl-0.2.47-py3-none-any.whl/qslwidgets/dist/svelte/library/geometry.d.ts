import type { Point, Dimensions, PolygonLabel } from "./types.js";
export declare const getDistance: (pt1: Point, pt2: Point, dimensions?: Dimensions) => number;
export declare const isPolygonClosed: (candidate: Point, points?: Point[]) => boolean;
export declare const snap: (cursor: Point, polygon: PolygonLabel, dimensions: Dimensions) => Point;
export declare const convertCoordinates: (point: Point, element: HTMLElement | null) => Point;
export declare const mat2str: (mat: number[][]) => string;
export declare const simplify: (raw: Point[], cursor?: Point) => {
    points: Point[];
    xmin: number;
    ymin: number;
    xmax: number;
    ymax: number;
};
export declare const destructureAffineTransform: (mat: number[][]) => {
    cos: number;
    sin: number;
    tx: number;
    ty: number;
};
export declare const invertAffineTransform: (mat: number[][]) => number[][];
export declare const project: (mat: number[][], point: Point) => {
    x: number;
    y: number;
};
