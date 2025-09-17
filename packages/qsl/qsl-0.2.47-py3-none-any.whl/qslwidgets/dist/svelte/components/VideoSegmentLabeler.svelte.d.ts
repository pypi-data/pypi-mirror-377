import { SvelteComponent } from "svelte";
import type { TimestampedLabelWithMatch, VideoSegmentTarget, WidgetActions, Config, TimestampedLabel, ArbitraryMetadata } from "../library/types.js";
declare const __propDef: {
    props: {
        target: VideoSegmentTarget | undefined;
        transitioning?: boolean;
        metadata?: ArbitraryMetadata | undefined;
        editableConfig?: boolean;
        labels: (TimestampedLabelWithMatch | TimestampedLabel)[] | undefined;
        config: Config;
        navigation?: boolean;
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
export type VideoSegmentLabelerProps = typeof __propDef.props;
export type VideoSegmentLabelerEvents = typeof __propDef.events;
export type VideoSegmentLabelerSlots = typeof __propDef.slots;
export default class VideoSegmentLabeler extends SvelteComponent<VideoSegmentLabelerProps, VideoSegmentLabelerEvents, VideoSegmentLabelerSlots> {
}
export {};
