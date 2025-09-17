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
export type TimeSeriesLabelerProps = typeof __propDef.props;
export type TimeSeriesLabelerEvents = typeof __propDef.events;
export type TimeSeriesLabelerSlots = typeof __propDef.slots;
export default class TimeSeriesLabeler extends SvelteComponent<TimeSeriesLabelerProps, TimeSeriesLabelerEvents, TimeSeriesLabelerSlots> {
}
export {};
