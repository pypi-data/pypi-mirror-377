import { SvelteComponent } from "svelte";
import type { Config, DraftState, ControlMenuActions } from "../library/types.js";
declare const __propDef: {
    props: {
        actions: ControlMenuActions;
        editableConfig: boolean;
        config: Config;
        disabled: boolean;
        navigation: boolean;
        draft: DraftState;
        layout?: "horizontal" | "vertical";
        disableRegions?: boolean;
        configShortcuts?: {
            [key: string]: string;
        } | undefined;
        regions?: boolean;
    };
    events: {
        change: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        'pre-button controls': {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ControlMenuProps = typeof __propDef.props;
export type ControlMenuEvents = typeof __propDef.events;
export type ControlMenuSlots = typeof __propDef.slots;
export default class ControlMenu extends SvelteComponent<ControlMenuProps, ControlMenuEvents, ControlMenuSlots> {
}
export {};
