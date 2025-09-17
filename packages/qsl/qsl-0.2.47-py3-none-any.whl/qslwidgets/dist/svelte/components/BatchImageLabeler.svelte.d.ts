import { SvelteComponent } from "svelte";
import type { BatchEntry, Labels, Config, WidgetActions } from '../library/types.js';
declare const __propDef: {
    props: {
        labels: Labels;
        config: Config;
        states?: BatchEntry[];
        targets?: (string | undefined)[] | undefined;
        navigation?: boolean;
        editableConfig?: boolean;
        transitioning?: boolean;
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
export type BatchImageLabelerProps = typeof __propDef.props;
export type BatchImageLabelerEvents = typeof __propDef.events;
export type BatchImageLabelerSlots = typeof __propDef.slots;
export default class BatchImageLabeler extends SvelteComponent<BatchImageLabelerProps, BatchImageLabelerEvents, BatchImageLabelerSlots> {
}
export {};
