/** @typedef {typeof __propDef.props}  UncheckedProps */
/** @typedef {typeof __propDef.events}  UncheckedEvents */
/** @typedef {typeof __propDef.slots}  UncheckedSlots */
export default class Unchecked extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type UncheckedProps = typeof __propDef.props;
export type UncheckedEvents = typeof __propDef.events;
export type UncheckedSlots = typeof __propDef.slots;
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
