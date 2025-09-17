import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        progress?: number | undefined;
        mode?: "dark" | "light";
        stores?: import("../library/types").SharedStores;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type LabelerProps = typeof __propDef.props;
export type LabelerEvents = typeof __propDef.events;
export type LabelerSlots = typeof __propDef.slots;
export default class Labeler extends SvelteComponent<LabelerProps, LabelerEvents, LabelerSlots> {
}
export {};
