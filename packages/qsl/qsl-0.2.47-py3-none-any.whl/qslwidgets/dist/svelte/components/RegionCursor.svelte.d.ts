import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        x: number;
        y: number;
        radius: number;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type RegionCursorProps = typeof __propDef.props;
export type RegionCursorEvents = typeof __propDef.events;
export type RegionCursorSlots = typeof __propDef.slots;
export default class RegionCursor extends SvelteComponent<RegionCursorProps, RegionCursorEvents, RegionCursorSlots> {
}
export {};
