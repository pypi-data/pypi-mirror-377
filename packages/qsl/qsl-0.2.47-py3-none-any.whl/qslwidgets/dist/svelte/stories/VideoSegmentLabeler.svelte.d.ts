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
export type VideoSegmentLabelerProps = typeof __propDef.props;
export type VideoSegmentLabelerEvents = typeof __propDef.events;
export type VideoSegmentLabelerSlots = typeof __propDef.slots;
export default class VideoSegmentLabeler extends SvelteComponent<VideoSegmentLabelerProps, VideoSegmentLabelerEvents, VideoSegmentLabelerSlots> {
}
export {};
