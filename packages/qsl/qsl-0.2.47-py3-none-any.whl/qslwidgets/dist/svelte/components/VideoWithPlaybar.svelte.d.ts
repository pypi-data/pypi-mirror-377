import { SvelteComponent } from "svelte";
import type { RangeSliderMark } from "../library/types.js";
declare const __propDef: {
    props: {
        target: string;
        t1: number | undefined;
        t2: number | undefined;
        playhead?: number;
        paused?: boolean;
        muted?: boolean;
        limitToBounds?: boolean;
        marks?: RangeSliderMark[];
        disabled?: boolean;
    };
    events: {
        setMarkers: CustomEvent<{
            t1: number;
            t2: number | undefined;
        }>;
        loaded: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type VideoWithPlaybarProps = typeof __propDef.props;
export type VideoWithPlaybarEvents = typeof __propDef.events;
export type VideoWithPlaybarSlots = typeof __propDef.slots;
export default class VideoWithPlaybar extends SvelteComponent<VideoWithPlaybarProps, VideoWithPlaybarEvents, VideoWithPlaybarSlots> {
}
export {};
