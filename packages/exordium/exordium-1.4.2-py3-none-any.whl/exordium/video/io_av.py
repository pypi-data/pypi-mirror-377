import av


class VideoWriter:

    def __init__(self, path, frame_rate, bit_rate=1000000):
        self.container = av.open(path, mode='w')
        self.stream = self.container.add_stream('h264', rate=f'{frame_rate:.4f}')
        self.stream.pix_fmt = 'yuv420p'
        self.stream.bit_rate = bit_rate

    def write(self, frames):
        # frames == (T,C,H,W)
        self.stream.width = frames.size(3)
        self.stream.height = frames.size(2)

        # convert grayscale to RGB
        if frames.size(1) == 1:
            frames = frames.repeat(1, 3, 1, 1)

        frames = frames.mul(255).byte().cpu().permute(0, 2, 3, 1).numpy()

        for t in range(frames.shape[0]):
            frame = frames[t]
            frame = av.VideoFrame.from_ndarray(frame, format='rgb24')
            self.container.mux(self.stream.encode(frame))

    def close(self):
        self.container.mux(self.stream.encode())
        self.container.close()
