import { SvelteComponent } from "svelte";
import type { LabelConfig } from '../library/types.js';
declare const __propDef: {
    props: {
        config: LabelConfig;
        disabled: boolean;
        selected: string[] | undefined;
        shortcut?: string | undefined;
        editableConfig: boolean;
    };
    events: {
        editConfig: CustomEvent<any>;
        change: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type LabelPanelEntryProps = typeof __propDef.props;
export type LabelPanelEntryEvents = typeof __propDef.events;
export type LabelPanelEntrySlots = typeof __propDef.slots;
export default class LabelPanelEntry extends SvelteComponent<LabelPanelEntryProps, LabelPanelEntryEvents, LabelPanelEntrySlots> {
}
export {};
