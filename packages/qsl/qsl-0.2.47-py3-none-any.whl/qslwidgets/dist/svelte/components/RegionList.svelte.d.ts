import { SvelteComponent } from "svelte";
import type { Point, DrawingState, DraftLabels, ImageData, Dimensions, StackContentLayer, Config } from "../library/types.js";
declare const __propDef: {
    props: {
        labels: DraftLabels;
        config: Config;
        drawing: DrawingState;
        cursor?: Point | undefined;
        target: HTMLImageElement | HTMLVideoElement;
        image?: ImageData | null;
        transform?: {
            size: Dimensions;
            layer: StackContentLayer;
        } | undefined;
        maxCanvasSize: number;
    };
    events: {
        change: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type RegionListProps = typeof __propDef.props;
export type RegionListEvents = typeof __propDef.events;
export type RegionListSlots = typeof __propDef.slots;
export default class RegionList extends SvelteComponent<RegionListProps, RegionListEvents, RegionListSlots> {
}
export {};
