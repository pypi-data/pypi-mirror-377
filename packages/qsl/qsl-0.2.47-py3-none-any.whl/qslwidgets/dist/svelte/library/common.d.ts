import type { Config, AlignedBoxLabel, Labels, DraftLabels, TimestampedLabel, LabelConfig, LabelData, Point, Bitmap, MediaLoadState, DraftState, TimestampInfoWithMatch, Dimensions, TimestampInfo } from "./types.js";
export declare const pct2css: (pct: number) => string;
export declare const insertOrAppend: <T>(arr: T[], item: T, idx: number, save: boolean) => T[];
export declare const copy: (o: any) => any;
export declare const labels2string: (labels: {
    [key: string]: string[];
}) => string;
export declare const epsilon = 0.0001;
export declare const labels2draft: (labels?: Labels) => DraftLabels;
export declare const sortBoxPoints: (box: AlignedBoxLabel) => AlignedBoxLabel;
export declare const draft2labels: (labels: DraftLabels) => Labels;
export declare const insertOrAppendByTimestamp: (current: TimestampedLabel, existing: TimestampedLabel[]) => TimestampedLabel[];
export declare const shortcutify: (initial: LabelConfig[]) => LabelConfig[];
export declare const computeDefaultRegionLabels: (config: Config) => LabelData;
export declare const renderBitmapToCanvas: (bitmap: Bitmap, canvas: HTMLCanvasElement, color: "red" | "blue" | "yellow") => boolean;
export declare const buildOptions: (selected: string[] | undefined, config: LabelConfig) => undefined | {
    name: string;
    shortcut: string;
    label: string;
    selected?: boolean;
}[];
export declare const delay: (amount: number) => Promise<unknown>;
export declare const simulateClick: (target: HTMLElement | null, offset?: Point) => Promise<void>;
export declare const findFocusTarget: (element: HTMLElement) => Element | null;
export declare const elementIsFocused: (element: HTMLElement, target?: EventTarget | null) => boolean;
export declare const focus: (element?: HTMLElement) => boolean;
export declare const processSelectionChange: <T>(value: T, selected: T[] | undefined, multiple: boolean, required?: boolean, options?: boolean) => T[];
export declare const createContentLoader: <T, V>(options: {
    targets: (V | undefined)[];
    load: (event: any, target: V | undefined) => Promise<T>;
}) => {
    callbacks: {
        load: (event: Event) => Promise<void>;
        error: () => void;
    }[];
    promise: Promise<{
        targets: (V | undefined)[];
        loadState: MediaLoadState;
        mediaState: undefined | {
            states: T[];
        };
    }>;
    state: import("svelte/store").Readable<{
        targets: (V | undefined)[];
        loadState: MediaLoadState;
        mediaState: undefined | {
            states: T[];
        };
    }>;
};
export declare const undoable: <T>(initial: T, serialize?: (current: T) => T, deserialize?: (value: T) => T, destroy?: (remove: T[], keep: T[]) => void, length?: number, debounce?: number) => {
    history: {
        undo: () => void;
        subscribe: (subscriber: (state: number) => void) => () => boolean;
    };
    state: {
        set: (update: T) => void;
        snapshot: () => void;
        reset: (update: T) => void;
        subscribe: (subscriber: (state: T) => void) => () => boolean;
    };
};
export declare const emptyDraftState: DraftState;
export declare const createDraftStore: () => {
    history: {
        undo: () => void;
        subscribe: (subscriber: (state: number) => void) => () => boolean;
    };
    draft: {
        reset: (labels: Labels, timestampInfo?: TimestampInfo | TimestampInfoWithMatch) => void;
        export: (dimensions?: Dimensions) => {
            dimensions: Dimensions | undefined;
            image?: LabelData;
            polygons?: import("./types.js").PolygonLabel[];
            masks?: import("./types.js").MaskLabel<import("./types.js").RLEMap>[];
            boxes?: AlignedBoxLabel[];
        };
        set: (update: DraftState) => void;
        snapshot: () => void;
        subscribe: (subscriber: (state: DraftState) => void) => () => boolean;
    };
};
export declare const labels4timestamp: (labels: TimestampedLabel[], timestamp: number) => {
    label: TimestampedLabel;
    exists: boolean;
};
