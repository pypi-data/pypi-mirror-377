/** @typedef {typeof __propDef.props}  MutedProps */
/** @typedef {typeof __propDef.events}  MutedEvents */
/** @typedef {typeof __propDef.slots}  MutedSlots */
export default class Muted extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type MutedProps = typeof __propDef.props;
export type MutedEvents = typeof __propDef.events;
export type MutedSlots = typeof __propDef.slots;
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
