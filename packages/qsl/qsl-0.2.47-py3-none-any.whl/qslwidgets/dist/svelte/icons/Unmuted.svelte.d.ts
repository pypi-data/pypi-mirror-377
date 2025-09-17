/** @typedef {typeof __propDef.props}  UnmutedProps */
/** @typedef {typeof __propDef.events}  UnmutedEvents */
/** @typedef {typeof __propDef.slots}  UnmutedSlots */
export default class Unmuted extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type UnmutedProps = typeof __propDef.props;
export type UnmutedEvents = typeof __propDef.events;
export type UnmutedSlots = typeof __propDef.slots;
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
