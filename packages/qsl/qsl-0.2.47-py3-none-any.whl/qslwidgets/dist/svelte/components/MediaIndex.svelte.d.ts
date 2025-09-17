import { SvelteComponent } from "svelte";
import type { IndexState } from "../library/types.js";
declare class __sveltets_Render<T extends number | string> {
    props(): {
        indexState: IndexState<T>;
        idx: T;
    };
    events(): {
        label: CustomEvent<any>;
        sort: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots(): {};
}
export type MediaIndexProps<T extends number | string> = ReturnType<__sveltets_Render<T>['props']>;
export type MediaIndexEvents<T extends number | string> = ReturnType<__sveltets_Render<T>['events']>;
export type MediaIndexSlots<T extends number | string> = ReturnType<__sveltets_Render<T>['slots']>;
export default class MediaIndex<T extends number | string> extends SvelteComponent<MediaIndexProps<T>, MediaIndexEvents<T>, MediaIndexSlots<T>> {
}
export {};
