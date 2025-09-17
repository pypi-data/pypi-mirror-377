import { SvelteComponent } from "svelte";
import "nouislider/dist/nouislider.css";
import type { RangeSliderMark } from "../library/types.js";
declare const __propDef: {
    props: {
        name: string;
        value: number;
        min: number;
        max: number;
        step?: number;
        disabled: boolean | undefined;
        ariaLabel?: string;
        marks?: RangeSliderMark[];
    };
    events: {
        change: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type RangeSliderProps = typeof __propDef.props;
export type RangeSliderEvents = typeof __propDef.events;
export type RangeSliderSlots = typeof __propDef.slots;
export default class RangeSlider extends SvelteComponent<RangeSliderProps, RangeSliderEvents, RangeSliderSlots> {
}
export {};
