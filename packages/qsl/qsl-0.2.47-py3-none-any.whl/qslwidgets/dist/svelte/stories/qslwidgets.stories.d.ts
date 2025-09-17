import ImageLabeler from "./ImageLabeler.svelte";
import BatchImageLabeler from "./BatchImageLabeler.svelte";
import VideoLabeler from "./VideoLabeler.svelte";
import TimeSeriesLabeler from "./TimeSeriesLabeler.svelte";
import MediaIndex from "./MediaIndex.svelte";
import ImageGroupLabeler from "./ImageGroupLabeler.svelte";
import ImageStackLabeler from "./ImageStackLabeler.svelte";
import VideoSegmentLabeler from "./VideoSegmentLabeler.svelte";
declare const _default: {
    title: string;
    argTypes: {};
};
export default _default;
export declare const SingleImage: () => {
    Component: typeof ImageLabeler;
};
export declare const BatchedImages: () => {
    Component: typeof BatchImageLabeler;
};
export declare const Video: () => {
    Component: typeof VideoLabeler;
};
export declare const Time: () => {
    Component: typeof TimeSeriesLabeler;
};
export declare const ImageGroup: () => {
    Component: typeof ImageGroupLabeler;
};
export declare const ImageStack: () => {
    Component: typeof ImageStackLabeler;
};
export declare const VideoSegment: () => {
    Component: typeof VideoSegmentLabeler;
};
export declare const Index: () => {
    Component: typeof MediaIndex;
};
