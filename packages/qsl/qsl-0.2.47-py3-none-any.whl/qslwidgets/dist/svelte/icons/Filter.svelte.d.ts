/** @typedef {typeof __propDef.props}  FilterProps */
/** @typedef {typeof __propDef.events}  FilterEvents */
/** @typedef {typeof __propDef.slots}  FilterSlots */
export default class Filter extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type FilterProps = typeof __propDef.props;
export type FilterEvents = typeof __propDef.events;
export type FilterSlots = typeof __propDef.slots;
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
