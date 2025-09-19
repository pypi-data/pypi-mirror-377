#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "main.cpp"

namespace py = pybind11;


py::dict py_get_chr_sizes(const std::string& genome) {
    return py::cast(get_chr_sizes(genome));
}


class PyBigwigReader {
    std::shared_ptr<BigwigReader> reader;

public:
    py::dict main_header;
    py::list zoom_headers;
    py::dict total_summary;
    py::dict chr_tree_header;
    py::dict chr_sizes;

    PyBigwigReader(const std::string& path, uint64_t parallel = 0) {
        reader = std::make_shared<BigwigReader>(path, parallel);
        auto headers_future = reader->read_headers();
        headers_future.get();

        main_header[py::str("magic")] = reader->main_header.magic;
        main_header[py::str("version")] = reader->main_header.version;
        main_header[py::str("zoom_levels")] = reader->main_header.zoom_levels;
        main_header[py::str("chr_tree_offset")] = reader->main_header.chr_tree_offset;
        main_header[py::str("full_data_offset")] = reader->main_header.full_data_offset;
        main_header[py::str("full_index_offset")] = reader->main_header.full_index_offset;
        main_header[py::str("field_count")] = reader->main_header.field_count;
        main_header[py::str("defined_field_count")] = reader->main_header.defined_field_count;
        main_header[py::str("auto_sql_offset")] = reader->main_header.auto_sql_offset;
        main_header[py::str("total_summary_offset")] = reader->main_header.total_summary_offset;
        main_header[py::str("uncompress_buffer_size")] = reader->main_header.uncompress_buffer_size;
        main_header[py::str("reserved")] = reader->main_header.reserved;

        total_summary[py::str("bases_covered")] = reader->total_summary.bases_covered;
        total_summary[py::str("min_value")] = reader->total_summary.min_value;
        total_summary[py::str("max_value")] = reader->total_summary.max_value;
        total_summary[py::str("sum_data")] = reader->total_summary.sum_data;
        total_summary[py::str("sum_squared")] = reader->total_summary.sum_squared;

        chr_tree_header[py::str("magic")] = reader->chr_tree_header.magic;
        chr_tree_header[py::str("block_size")] = reader->chr_tree_header.block_size;
        chr_tree_header[py::str("key_size")] = reader->chr_tree_header.key_size;
        chr_tree_header[py::str("value_size")] = reader->chr_tree_header.value_size;
        chr_tree_header[py::str("item_count")] = reader->chr_tree_header.item_count;
        chr_tree_header[py::str("reserved")] = reader->chr_tree_header.reserved;

        for (const auto& zoom_header : reader->zoom_headers) {
            py::dict zoom_header_dict;
            zoom_header_dict[py::str("reduction_level")] = zoom_header.reduction_level;
            zoom_header_dict[py::str("reserved")] = zoom_header.reserved;
            zoom_header_dict[py::str("data_offset")] = zoom_header.data_offset;
            zoom_header_dict[py::str("index_offset")] = zoom_header.index_offset;
            zoom_headers.append(zoom_header_dict);
        }
        
        for (const auto& chr : reader->chr_map) {
            chr_sizes[py::str(chr.first)] = chr.second.chr_size;
        }
    }
    
    py::array_t<float> read_values(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        uint64_t span,
        uint64_t resolution = 1,
        float default_value = 0.0f,
        bool use_zoom = true,
        py::object progress = py::none()) {

        std::function<void(uint64_t, uint64_t)> progress_callback = nullptr;
        if (!progress.is_none()) {
            progress_callback = [progress](uint64_t current, uint64_t total) {
                progress(current, total);
            };
        }

        auto values = reader->read_values(
            chr_ids, starts, span, resolution, default_value, use_zoom, progress_callback
        );
        
        // Convert to numpy array
        uint64_t bin_count = (span + resolution - 1) / resolution;
        uint64_t row_count = chr_ids.size();
        uint64_t col_count = bin_count;
        std::vector<ssize_t> shape = {static_cast<ssize_t>(row_count), static_cast<ssize_t>(col_count)};
        std::vector<ssize_t> strides = {static_cast<ssize_t>(col_count * sizeof(float)), static_cast<ssize_t>(sizeof(float))};
        return py::array_t<float>(shape, strides, values.data());
    }

    void to_bedgraph(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        reader->to_bedgraph(output_path, chr_ids, zoom_level);
    }
    
    void to_wig(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        reader->to_wig(output_path, chr_ids, zoom_level);
    }

};


PYBIND11_MODULE(bigwig_io, m, py::mod_gil_not_used()) {
    m.doc() = "Python bindings for bigwig_io C++ library";

    m.def("get_chr_sizes", &py_get_chr_sizes, "Get chromosome sizes for a given genome",
          py::arg("genome"));

    py::class_<PyBigwigReader>(m, "BigwigReader")
        .def(py::init<const std::string&, uint64_t>(), "Create a BigWig reader from file path",
             py::arg("path"), py::arg("parallel") = 0)
        .def_readonly("main_header", &PyBigwigReader::main_header)
        .def_readonly("total_summary", &PyBigwigReader::total_summary)
        .def_readonly("chr_tree_header", &PyBigwigReader::chr_tree_header)
        .def_readonly("zoom_headers", &PyBigwigReader::zoom_headers)
        .def_readonly("chr_sizes", &PyBigwigReader::chr_sizes)
        .def("read_values", &PyBigwigReader::read_values,
             "Read values from BigWig file",
             py::arg("chr_ids"), py::arg("starts"), py::arg("span"), 
             py::arg("resolution") = 1, py::arg("default_value") = 0.0f,
             py::arg("use_zoom") = true,
             py::arg("progress") = py::none()
        )
        .def("to_bedgraph", &PyBigwigReader::to_bedgraph, 
             "Convert BigWig file to bedGraph format",
             py::arg("output_path"),
             py::arg("chr_ids") = std::vector<std::string>{},
             py::arg("zoom_level") = -1)
        .def("to_wig", &PyBigwigReader::to_wig,
             "Convert BigWig file to WIG format",
             py::arg("output_path"),
             py::arg("chr_ids") = std::vector<std::string>{},
             py::arg("zoom_level") = -1);


}
