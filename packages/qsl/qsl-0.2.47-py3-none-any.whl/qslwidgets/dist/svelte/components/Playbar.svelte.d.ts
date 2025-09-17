import { SvelteComponent } from "svelte";
import "nouislider/dist/nouislider.css";
import type { RangeSliderMark } from "../library/types.js";
declare const __propDef: {
    props: {
        mains?: HTMLVideoElement[];
        secondaries?: HTMLVideoElement[];
        disabled: boolean | undefined;
        marks?: RangeSliderMark[];
        limitToBounds?: boolean;
        duration?: number | undefined;
        playhead?: number;
        t1?: number | undefined;
        t2?: number | undefined;
        paused?: boolean;
        muted?: boolean;
    };
    slots: {};
    events: {
        setMarkers: CustomEvent<{
            t1: number;
            t2: number | undefined;
        }>;
    };
};
export type PlaybarProps = typeof __propDef.props;
export type PlaybarEvents = typeof __propDef.events;
export type PlaybarSlots = typeof __propDef.slots;
export default class Playbar extends SvelteComponent<PlaybarProps, PlaybarEvents, PlaybarSlots> {
}
export {};
