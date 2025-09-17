import { SvelteComponent } from "svelte";
import type { LabelConfig, LabelData } from "../library/types.js";
declare const __propDef: {
    props: {
        config: LabelConfig[];
        labels: LabelData;
        disabled: boolean;
        configShortcuts?: {
            [key: string]: string;
        } | undefined;
        editableConfig: boolean;
    };
    events: {
        change: CustomEvent<any>;
        editConfig: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type LabelPanelProps = typeof __propDef.props;
export type LabelPanelEvents = typeof __propDef.events;
export type LabelPanelSlots = typeof __propDef.slots;
export default class LabelPanel extends SvelteComponent<LabelPanelProps, LabelPanelEvents, LabelPanelSlots> {
}
export {};
