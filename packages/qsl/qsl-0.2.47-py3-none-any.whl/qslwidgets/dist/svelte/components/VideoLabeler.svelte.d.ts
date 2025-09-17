import { SvelteComponent } from "svelte";
import type { TimestampedLabel, Config, ArbitraryMetadata, WidgetActions } from "../library/types.js";
declare const __propDef: {
    props: {
        target: string | undefined;
        config: Config;
        labels: TimestampedLabel[];
        metadata?: ArbitraryMetadata;
        navigation?: boolean;
        editableConfig?: boolean;
        maxCanvasSize?: number;
        transitioning?: boolean;
        viewHeight?: number;
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
export type VideoLabelerProps = typeof __propDef.props;
export type VideoLabelerEvents = typeof __propDef.events;
export type VideoLabelerSlots = typeof __propDef.slots;
export default class VideoLabeler extends SvelteComponent<VideoLabelerProps, VideoLabelerEvents, VideoLabelerSlots> {
}
export {};
