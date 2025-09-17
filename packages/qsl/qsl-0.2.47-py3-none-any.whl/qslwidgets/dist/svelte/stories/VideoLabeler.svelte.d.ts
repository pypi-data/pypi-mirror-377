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
export type VideoLabelerProps = typeof __propDef.props;
export type VideoLabelerEvents = typeof __propDef.events;
export type VideoLabelerSlots = typeof __propDef.slots;
export default class VideoLabeler extends SvelteComponent<VideoLabelerProps, VideoLabelerEvents, VideoLabelerSlots> {
}
export {};
