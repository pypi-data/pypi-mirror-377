import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type FocusIndicatorProps = typeof __propDef.props;
export type FocusIndicatorEvents = typeof __propDef.events;
export type FocusIndicatorSlots = typeof __propDef.slots;
export default class FocusIndicator extends SvelteComponent<FocusIndicatorProps, FocusIndicatorEvents, FocusIndicatorSlots> {
}
export {};
