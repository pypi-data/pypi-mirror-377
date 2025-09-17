import { SvelteComponent } from "svelte";
import type { Bitmap } from "../library/types.js";
declare const __propDef: {
    props: {
        bitmap: Bitmap;
        color: "red" | "blue" | "yellow";
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type RegionMaskProps = typeof __propDef.props;
export type RegionMaskEvents = typeof __propDef.events;
export type RegionMaskSlots = typeof __propDef.slots;
export default class RegionMask extends SvelteComponent<RegionMaskProps, RegionMaskEvents, RegionMaskSlots> {
}
export {};
