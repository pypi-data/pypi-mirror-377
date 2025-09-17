import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        size?: string | number;
        unit?: string;
        colorOuter?: string;
        colorCenter?: string;
        colorInner?: string;
        durationMultiplier?: number;
        durationOuter?: string;
        durationInner?: string;
        durationCenter?: string;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type SpinnerProps = typeof __propDef.props;
export type SpinnerEvents = typeof __propDef.events;
export type SpinnerSlots = typeof __propDef.slots;
export default class Spinner extends SvelteComponent<SpinnerProps, SpinnerEvents, SpinnerSlots> {
}
export {};
