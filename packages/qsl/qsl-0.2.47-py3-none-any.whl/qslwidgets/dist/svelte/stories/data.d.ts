import type { Config, Labels, TimestampedLabel, IndexState, TimeSeriesTarget } from "../library/types";
export declare const images: {
    url: string | undefined;
    labels: Labels;
    metadata?: {
        [key: string]: string;
    };
}[];
export declare const videos: {
    url: string;
    labels: TimestampedLabel[];
}[];
export declare const config: Config;
export declare const indexState: IndexState<number>;
export declare const timeSeries: TimeSeriesTarget[];
export declare const timeSeriesConfig: {
    image: {
        name: string;
        freeform: boolean;
        multiple: boolean;
    }[];
};
