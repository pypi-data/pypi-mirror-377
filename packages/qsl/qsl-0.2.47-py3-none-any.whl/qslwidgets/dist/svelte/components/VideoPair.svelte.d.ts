import { SvelteComponent } from "svelte";
import type { DraftState, VideoSegmentTarget } from "../library/types.js";
declare const __propDef: {
    props: {
        target: VideoSegmentTarget;
        draft: DraftState;
        playbackState: {
            video1: {
                paused: boolean;
                playhead: number;
            };
            video2: {
                paused: boolean;
                playhead: number;
            };
        };
    };
    events: {
        'loaded-video1': CustomEvent<any>;
        change: CustomEvent<any>;
        'loaded-video2': CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type VideoPairProps = typeof __propDef.props;
export type VideoPairEvents = typeof __propDef.events;
export type VideoPairSlots = typeof __propDef.slots;
export default class VideoPair extends SvelteComponent<VideoPairProps, VideoPairEvents, VideoPairSlots> {
}
export {};
