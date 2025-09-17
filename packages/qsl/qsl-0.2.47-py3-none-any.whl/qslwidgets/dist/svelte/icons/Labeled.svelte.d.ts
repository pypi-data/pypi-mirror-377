/** @typedef {typeof __propDef.props}  LabeledProps */
/** @typedef {typeof __propDef.events}  LabeledEvents */
/** @typedef {typeof __propDef.slots}  LabeledSlots */
export default class Labeled extends SvelteComponent<{
    [x: string]: never;
}, {
    [evt: string]: CustomEvent<any>;
}, {}> {
}
export type LabeledProps = typeof __propDef.props;
export type LabeledEvents = typeof __propDef.events;
export type LabeledSlots = typeof __propDef.slots;
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
