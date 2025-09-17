import { SvelteComponent } from "svelte";
import type { Config, Labels, WidgetActions, ArbitraryMetadata, TimeSeriesTarget } from "../library/types.js";
declare const __propDef: {
    props: {
        target: TimeSeriesTarget | undefined;
        config: Config;
        labels: Labels;
        metadata?: ArbitraryMetadata;
        navigation?: boolean;
        editableConfig?: boolean;
        transitioning?: boolean;
        viewHeight?: number | null;
        fixedHeight?: boolean;
        actions?: WidgetActions;
    };
    events: {
        next: CustomEvent<any>;
        prev: CustomEvent<any>;
        delete: CustomEvent<any>;
        ignore: CustomEvent<any>;
        unignore: CustomEvent<any>;
        showIndex: CustomEvent<any>;
        save: CustomEvent<any>;
    } & {
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
