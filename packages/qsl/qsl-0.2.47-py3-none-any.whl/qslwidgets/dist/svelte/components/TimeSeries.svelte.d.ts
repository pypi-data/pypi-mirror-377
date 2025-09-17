import { SvelteComponent } from "svelte";
import type { TimeSeriesTarget, Dimensions, DraftLabels, Config } from "../library/types.js";
declare const __propDef: {
    props: {
        target: TimeSeriesTarget | undefined;
        config: Config;
        labels: DraftLabels;
        defaultWidth?: undefined | number;
        chartSize?: Dimensions | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type TimeSeriesProps = typeof __propDef.props;
export type TimeSeriesEvents = typeof __propDef.events;
export type TimeSeriesSlots = typeof __propDef.slots;
export default class TimeSeries extends SvelteComponent<TimeSeriesProps, TimeSeriesEvents, TimeSeriesSlots> {
}
export {};
