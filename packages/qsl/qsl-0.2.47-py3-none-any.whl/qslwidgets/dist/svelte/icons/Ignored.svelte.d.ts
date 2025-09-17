/** @typedef {typeof __propDef.props}  IgnoredProps */
/** @typedef {typeof __propDef.events}  IgnoredEvents */
/** @typedef {typeof __propDef.slots}  IgnoredSlots */
export default class Ignored extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type IgnoredProps = typeof __propDef.props;
export type IgnoredEvents = typeof __propDef.events;
export type IgnoredSlots = typeof __propDef.slots;
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
