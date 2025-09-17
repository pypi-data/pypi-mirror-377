/** @typedef {typeof __propDef.props}  CheckedProps */
/** @typedef {typeof __propDef.events}  CheckedEvents */
/** @typedef {typeof __propDef.slots}  CheckedSlots */
export default class Checked extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type CheckedProps = typeof __propDef.props;
export type CheckedEvents = typeof __propDef.events;
export type CheckedSlots = typeof __propDef.slots;
import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        [x: string]: never;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: undefined;
    bindings?: undefined;
};
export {};
