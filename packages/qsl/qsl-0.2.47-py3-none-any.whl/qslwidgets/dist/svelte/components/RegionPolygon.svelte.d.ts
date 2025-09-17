import { SvelteComponent } from "svelte";
import type { Point, PolygonLabel } from "../library/types.js";
declare const __propDef: {
    props: {
        polygon: PolygonLabel;
        color: string;
        candidate?: Point | undefined;
    };
    events: {
        click: PointerEvent;
        mousemove: MouseEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type RegionPolygonProps = typeof __propDef.props;
export type RegionPolygonEvents = typeof __propDef.events;
export type RegionPolygonSlots = typeof __propDef.slots;
export default class RegionPolygon extends SvelteComponent<RegionPolygonProps, RegionPolygonEvents, RegionPolygonSlots> {
}
export {};
