import { SvelteComponent } from "svelte";
import type { Extractor } from "../library/types.js";
declare const __propDef: {
    props: {
        extract: Extractor;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type WidgetProps = typeof __propDef.props;
export type WidgetEvents = typeof __propDef.events;
export type WidgetSlots = typeof __propDef.slots;
export default class Widget extends SvelteComponent<WidgetProps, WidgetEvents, WidgetSlots> {
}
export {};
