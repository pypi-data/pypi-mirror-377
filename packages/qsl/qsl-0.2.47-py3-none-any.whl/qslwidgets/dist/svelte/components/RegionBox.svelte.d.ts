import { SvelteComponent } from "svelte";
import type { AlignedBoxLabel, Point } from "../library/types.js";
declare const __propDef: {
    props: {
        box: AlignedBoxLabel;
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
export type RegionBoxProps = typeof __propDef.props;
export type RegionBoxEvents = typeof __propDef.events;
export type RegionBoxSlots = typeof __propDef.slots;
export default class RegionBox extends SvelteComponent<RegionBoxProps, RegionBoxEvents, RegionBoxSlots> {
}
export {};
