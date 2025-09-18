import typing

import numpy as np


class VirtualMap:
    """
    Virtual concatenation class for numpy arrays. List elements are indexed according to their order
    within their array and the order of the arrays. Slicing is supported, but only for a step of 1.
    Slicing between two arrays forces concatenation of the elements to be grouped and so a copy of
    these elements.
    """

    def __init__(self, arrays: typing.Sequence[np.ndarray]):
        VirtualMap._check_arrays(arrays)
        self.arrays: typing.Sequence[np.ndarray] = arrays
        """The numpy array to virtually concatenate."""
        self._cumulated_size = np.cumsum([a.shape[0] for a in arrays])
        self._offsets = [self._cumulated_size[index] for index in range(0, len(self._cumulated_size)-1)]
        self._offsets.insert(0, 0)
        shape = list()
        shape.append(int(self._cumulated_size[-1]))
        shape.extend([int(dim) for dim in self.arrays[0].shape[1:]])
        self.shape: tuple[int, ...] = tuple(shape)

    def __len__(self) -> int:
        return self._cumulated_size[-1]

    def __getitem__(self, index: int | np.signedinteger | slice) -> typing.Any | np.ndarray:
        if isinstance(index, (int, np.signedinteger)):
            if index < 0:
                index += len(self)
            if index < 0 or index >= len(self):
                raise IndexError("Index out of range")
            array_index = int(np.searchsorted(self._cumulated_size, index, side='right'))
            local_index = index - self._offsets[array_index]
            return self.arrays[array_index][local_index]
        elif isinstance(index, slice):  # TODO: shortcut when slice is all!
            start_index, stop_index, step = index.indices(self.__len__())
            if step != 1:
                raise NotImplementedError('steps different to 1 are not supported yet')
            current_index = start_index
            chunks: list[np.ndarray] = list()
            while current_index < stop_index - 1:
                array_index = int(np.searchsorted(self._cumulated_size, current_index, side='right'))
                local_index_stop = min(self.arrays[array_index].shape[0],
                                       stop_index - self._offsets[array_index])
                local_index_start = current_index - self._offsets[array_index]
                chunks.append(self.arrays[array_index][local_index_start: local_index_stop])
                current_index += local_index_stop - local_index_start
            if chunks:
                if len(chunks) == 1:
                    result = chunks[0]
                else:
                    result = np.concatenate(chunks)
            else:
                result = np.empty(0)
            return result
        else:
            raise TypeError(f'Index must be int or slice. Got: {type(index)}')

    @staticmethod
    def _check_arrays(arrays: typing.Sequence[np.ndarray]) -> None:
        if arrays:
            for array in arrays:
                if array.shape[0] == 0:
                    raise ValueError('empty array')
        else:
            raise ValueError('empty list of arrays')
