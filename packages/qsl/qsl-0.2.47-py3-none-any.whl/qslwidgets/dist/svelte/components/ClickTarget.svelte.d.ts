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
export type ClickTargetProps = typeof __propDef.props;
export type ClickTargetEvents = typeof __propDef.events;
export type ClickTargetSlots = typeof __propDef.slots;
export default class ClickTarget extends SvelteComponent<ClickTargetProps, ClickTargetEvents, ClickTargetSlots> {
}
export {};
