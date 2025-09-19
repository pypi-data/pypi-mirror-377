#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <deque>
#include <fstream>
#include <functional>
#include <future>
#include <map>
#include <mutex>
#include <string>
#include <tuple>
#include <vector>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"


MainHeader read_main_header(BufferedFile& file) {
    ByteArray buffer = file.read(64, 0);
    
    MainHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic == 0x26FC8F88) throw std::runtime_error("incompatible endianness");
    if (header.magic != 0x888FFC26) throw std::runtime_error("not a bigwig file");
    header.version = buffer.read_uint16(4);
    if (header.version < 3) throw std::runtime_error("bigwig version " + std::to_string(header.version) + " unsupported (>= 3)");
    header.zoom_levels = buffer.read_uint16(6);
    header.chr_tree_offset = buffer.read_uint64(8);
    header.full_data_offset = buffer.read_uint64(16);
    header.full_index_offset = buffer.read_uint64(24);
    header.field_count = buffer.read_uint16(32);
    header.defined_field_count = buffer.read_uint16(34);
    header.auto_sql_offset = buffer.read_uint64(36);
    header.total_summary_offset = buffer.read_uint64(44);
    header.uncompress_buffer_size = buffer.read_uint32(52);
    header.reserved = buffer.read_uint64(56);
    
    return header;
}


std::vector<ZoomHeader> read_zoom_headers(BufferedFile& file, uint16_t zoom_levels) {
    std::vector<ZoomHeader> headers;
    ByteArray buffer = file.read(zoom_levels * 24, 64);
    
    for (uint16_t i = 0; i < zoom_levels; ++i) {
        ZoomHeader header;
        header.reduction_level = buffer.read_uint32(i * 24);
        header.reserved = buffer.read_uint32(i * 24 + 4);
        header.data_offset = buffer.read_uint64(i * 24 + 8);
        header.index_offset = buffer.read_uint64(i * 24 + 16);
        headers.push_back(header);
    }
    
    return headers;
}


TotalSummary read_total_summary(BufferedFile& file, uint64_t offset) {
    ByteArray buffer = file.read(40, offset);
    
    TotalSummary summary;
    summary.bases_covered = buffer.read_uint64(0);
    summary.min_value = buffer.read_double(8);
    summary.max_value = buffer.read_double(16);
    summary.sum_data = buffer.read_double(24);
    summary.sum_squared = buffer.read_double(32);
    
    return summary;
}


ChrTreeHeader read_chr_tree_header(BufferedFile& file, uint64_t offset) {
    ByteArray buffer = file.read(32, offset);
    
    ChrTreeHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic == 0x91CA8C78) throw std::runtime_error("incompatible endianness (chromosome tree)");
    if (header.magic != 0x78CA8C91) throw std::runtime_error("invalid chromosome tree magic");
    header.block_size = buffer.read_uint32(4);
    header.key_size = buffer.read_uint32(8);
    header.value_size = buffer.read_uint32(12);
    header.item_count = buffer.read_uint64(16);
    header.reserved = buffer.read_uint64(24);

    return header;
}


std::vector<ChrTreeLeaf> read_chr_tree(BufferedFile& file, uint64_t offset, uint32_t key_size) {
    std::vector<ChrTreeLeaf> leaves;
    ByteArray header_buffer = file.read(4, offset);

    ChrTreeNodeHeader node_header;
    node_header.is_leaf = header_buffer.read_uint8(0);
    node_header.reserved = header_buffer.read_uint8(1);
    node_header.count = header_buffer.read_uint16(2);

    offset += 4;
    for (uint16_t i = 0; i < node_header.count; ++i) {
        ByteArray buffer = file.read(key_size + 8, offset);
        if (node_header.is_leaf) {
            ChrTreeLeaf leaf;
            leaf.key = buffer.read_string(0, key_size);
            leaf.chr_index = buffer.read_uint32(key_size);
            leaf.chr_size = buffer.read_uint32(key_size + 4);
            leaves.push_back(leaf);
        } else {
            ChrTreeBranch branch;
            branch.key = buffer.read_string(0, key_size);
            branch.child_offset = buffer.read_uint64(key_size);
            auto child_leaves = read_chr_tree(file, branch.child_offset, key_size);
            leaves.insert(leaves.end(), child_leaves.begin(), child_leaves.end());
        }
        offset += key_size + 8;
    }

    std::sort(leaves.begin(), leaves.end(), [](const ChrTreeLeaf& a, const ChrTreeLeaf& b) {
        return a.chr_index < b.chr_index;
    });

    return leaves;
}


std::map<std::string, ChrTreeLeaf> convert_chr_tree_to_map(const std::vector<ChrTreeLeaf>& leaves) {
    std::map<std::string, ChrTreeLeaf> chr_map;
    for (const auto& leaf : leaves) {
        chr_map[leaf.key] = leaf;
    }
    return chr_map;
}


DataTreeHeader read_data_tree_header(BufferedFile& file, uint64_t offset) {
    ByteArray buffer = file.read(48, offset);
    
    DataTreeHeader header;
    header.magic = buffer.read_uint32(0);
    if (header.magic == 0x61A0C5A0) throw std::runtime_error("incompatible endianness (data tree)");
    if (header.magic != 0x2468ACE0) throw std::runtime_error("invalid data tree magic");
    header.block_size = buffer.read_uint32(4);
    header.item_count = buffer.read_uint64(8);
    header.start_chr_index = buffer.read_uint32(16);
    header.start_base = buffer.read_uint32(20);
    header.end_chr_index = buffer.read_uint32(24);
    header.end_base = buffer.read_uint32(28);
    header.end_file_offset = buffer.read_uint64(32);
    header.items_per_slot = buffer.read_uint32(40);
    header.reserved = buffer.read_uint8(44);
    
    return header;
}


std::vector<DataTreeLeaf> read_data_tree(BufferedFile& file, uint64_t offset) {
    std::vector<DataTreeLeaf> leaves;
    ByteArray header_buffer = file.read(4, offset);
    DataTreeNodeHeader node_header;
    node_header.is_leaf = header_buffer.read_uint8(0);
    node_header.reserved = header_buffer.read_uint8(1);
    node_header.count = header_buffer.read_uint16(2);
    uint64_t node_size = node_header.is_leaf ? 32 : 24;

    offset += 4;
    for (uint16_t i = 0; i < node_header.count; ++i) {
        ByteArray buffer = file.read(node_size, offset);
        if (node_header.is_leaf) {
            DataTreeLeaf leaf;
            leaf.start_chr_index = buffer.read_uint32(0);
            leaf.start_base = buffer.read_uint32(4);
            leaf.end_chr_index = buffer.read_uint32(8);
            leaf.end_base = buffer.read_uint32(12);
            leaf.data_offset = buffer.read_uint64(16);
            leaf.data_size = buffer.read_uint64(24);
            leaves.push_back(leaf);
        } else {
            DataTreeBranch branch;
            branch.start_chr_index = buffer.read_uint32(0);
            branch.start_base = buffer.read_uint32(4);
            branch.end_chr_index = buffer.read_uint32(8);
            branch.end_base = buffer.read_uint32(12);
            branch.data_offset = buffer.read_uint64(16);
            auto child_leaves = read_data_tree(file, branch.data_offset);
            leaves.insert(leaves.end(), child_leaves.begin(), child_leaves.end());
        }
        offset += node_size;
    }

    std::sort(leaves.begin(), leaves.end(), [](const DataTreeLeaf& a, const DataTreeLeaf& b) {
        return std::tie(a.start_chr_index, a.start_base) < std::tie(b.start_chr_index, b.start_base);
    });

    return leaves;
}


struct TreeNodeGeneratorState {
    uint64_t offset;
    uint8_t is_leaf;
    uint16_t node_count;
    uint64_t node_size;
    ByteArray buffer;
    uint64_t buffer_index;
    uint16_t node_index;
};

struct TreeNodeGeneratorNext {
    DataTreeLeaf node;
    uint64_t start_loc_index;
    uint64_t end_loc_index;
    bool done;
};

class TreeNodeGenerator {
    BufferedFile& file;
    std::vector<Loc> locs;
    uint64_t start_loc_index;
    uint64_t end_loc_index;
    std::deque<TreeNodeGeneratorState> states;

    TreeNodeGeneratorState parse_node_header(uint64_t offset) {
        ByteArray header_buffer = file.read(4, offset);
        uint8_t is_leaf = header_buffer.read_uint8(0);
        // uint8_t reserved = header_buffer.read_uint8(1);
        uint16_t count = header_buffer.read_uint16(2);
        uint64_t node_size = is_leaf ? 32 : 24;
        ByteArray buffer = file.read(node_size * count, offset + 4);
        return {offset, is_leaf, count, node_size, buffer, 0, 0};
    }

public:
    uint64_t coverage;

    TreeNodeGenerator(BufferedFile& f, const std::vector<Loc>& l, uint64_t offset)
        : file(f), locs(l) {
            start_loc_index = 0;
            end_loc_index = locs.size();
            coverage = 0;
            states.push_front(parse_node_header(offset));
        }

    TreeNodeGeneratorNext next() {
        while (!states.empty()) {
            TreeNodeGeneratorState& header = states.front();
            if (header.node_index == header.node_count) states.pop_front();
            while (header.node_index < header.node_count) {
                uint32_t start_chr_index = header.buffer.read_uint32(header.buffer_index);
                uint32_t start_base = header.buffer.read_uint32(header.buffer_index + 4);
                uint32_t end_chr_index = header.buffer.read_uint32(header.buffer_index + 8);
                uint32_t end_base = header.buffer.read_uint32(header.buffer_index + 12);

                uint64_t node_end_loc_index = start_loc_index;
                for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
                    Loc loc = locs[loc_index];
                    if (loc.chr_index < start_chr_index || (loc.chr_index == start_chr_index && loc.end <= start_base)) {
                        coverage += static_cast<uint64_t>(loc.end - loc.start);
                        start_loc_index += 1;
                        continue;
                    }
                    if (loc.chr_index > end_chr_index || (loc.chr_index == end_chr_index && loc.start > end_base)) {
                        break;
                    }
                    node_end_loc_index = loc_index + 1;
                }
                if (node_end_loc_index > start_loc_index) {
                    if (header.is_leaf) {
                        DataTreeLeaf node;
                        node.start_chr_index = start_chr_index;
                        node.start_base = start_base;
                        node.end_chr_index = end_chr_index;
                        node.end_base = end_base;
                        node.data_offset = header.buffer.read_uint64(header.buffer_index + 16);
                        node.data_size = header.buffer.read_uint64(header.buffer_index + 24);
                        header.buffer_index += header.node_size;
                        header.node_index += 1;
                        return {node, start_loc_index, node_end_loc_index, false};
                    } else {
                        uint64_t data_offset = header.buffer.read_uint64(header.buffer_index + 16);
                        header.buffer_index += header.node_size;
                        header.node_index += 1;
                        states.push_front(parse_node_header(data_offset));
                        break;
                    }
                } else {
                    header.buffer_index += header.node_size;
                    header.node_index += 1;
                }
            }
        }
        while (start_loc_index < end_loc_index) {
            Loc loc = locs[start_loc_index];
            coverage += static_cast<uint64_t>(loc.end - loc.start);
            start_loc_index += 1;
        }
        return {DataTreeLeaf(), 0, 0, true};
    }

};


bool fill_value_at_locs(
    const std::vector<Loc>& locs,
    std::vector<float>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    uint32_t start, uint32_t end, float value) {

    uint32_t bin_start = start / resolution;
    uint32_t bin_end = end / resolution;
    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        uint32_t loc_bin_start = loc.start / resolution;
        uint32_t loc_bin_end = loc.end / resolution;
        if (bin_start >= loc_bin_end) continue;
        no_more_overlap = false;
        if (bin_end <= loc_bin_start) break;
        uint32_t overlap_start = std::max(bin_start, loc_bin_start);
        uint32_t overlap_end = std::min(bin_end, loc_bin_end);
        for (uint32_t b = overlap_start; b < overlap_end; ++b) {
            values[loc.values_index + (b - loc_bin_start)] = value;
        }
    }
    return no_more_overlap;
}


WigDataHeader read_wig_data_header(const ByteArray& buffer) {
    WigDataHeader header;
    header.chr_index = buffer.read_uint32(0);
    header.chr_start = buffer.read_uint32(4);
    header.chr_end = buffer.read_uint32(8);
    header.item_step = buffer.read_uint32(12);
    header.item_span = buffer.read_uint32(16);
    header.type = buffer.read_uint8(20);
    header.reserved = buffer.read_uint8(21);
    header.item_count = buffer.read_uint16(22);
    return header;
}


ZoomDataRecord read_zoom_data_record(const ByteArray& buffer, uint64_t index) {
    uint64_t offset = index * 32;
    ZoomDataRecord record;
    record.chr_index = buffer.read_uint32(offset);
    record.chr_start = buffer.read_uint32(offset + 4);
    record.chr_end = buffer.read_uint32(offset + 8);
    record.valid_count = buffer.read_uint32(offset + 12);
    record.min_value = buffer.read_float(offset + 16);
    record.max_value = buffer.read_float(offset + 20);
    record.sum_data = buffer.read_float(offset + 24);
    record.sum_squared = buffer.read_float(offset + 28);
    return record;
}


void read_data_node_at_locs(
    BufferedFile& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<float>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset);
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    WigDataHeader header = read_wig_data_header(buffer);

    if (header.type == 1) { // bedGraph
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 12);
            uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
            float value = buffer.read_float(24 + i * 12 + 8);
                auto no_more_overlap = fill_value_at_locs(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 2) { // variableStep
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 8);
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 8 + 4);
                auto no_more_overlap = fill_value_at_locs(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 3) { // fixedStep
        if (resolution <= header.item_step) {
            for (uint16_t i = 0; i < header.item_count; ++i) {
                uint32_t start = header.chr_start + i * header.item_step;
                uint32_t end = start + header.item_span;
                float value = buffer.read_float(24 + i * 4);
                auto no_more_overlap = fill_value_at_locs(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
                if (no_more_overlap) break;
        }
        } else {
            double span_over_step = static_cast<double>(header.item_span) / header.item_step;
            for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
                const Loc& loc = locs[loc_index];
                uint32_t start = std::max(loc.start, header.chr_start);
                uint32_t end = std::min(loc.end, header.chr_end);
                uint32_t loc_bin_start = loc.start / resolution;
                for (uint32_t pos = start; pos < end; pos += resolution) {
                    double bin = (static_cast<double>(pos - header.chr_start)) / header.item_step;
                    uint32_t bin_index = static_cast<uint32_t>(bin);
                    if (bin_index >= header.item_count) break;
                    if (bin - bin_index > span_over_step) continue;
                    float value = buffer.read_float(24 + bin_index * 4);
                    uint32_t loc_bin = pos / resolution;
                    values[loc.values_index + (loc_bin - loc_bin_start)] = value;
                }
            }
        }
    } else {
        throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
    }

}


void read_zoom_data_node_at_locs(
    BufferedFile& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<float>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset);
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    uint64_t record_count = node.data_size / 32;
    for (uint64_t i = 0; i < record_count; ++i) {
        ZoomDataRecord record = read_zoom_data_record(buffer, i);
        if (record.valid_count > 0) {
            float mean_value = record.sum_data / record.valid_count;
            auto no_more_overlap = fill_value_at_locs(
                locs, values, start_loc_index, end_loc_index, resolution,
                record.chr_start, record.chr_end, mean_value
            );
            if (no_more_overlap) break;
        }
    }
}





class BigwigReader {
    std::string path;
    std::shared_ptr<BufferedFile> file;
    uint64_t parallel;

public:
    MainHeader main_header;
    std::vector<ZoomHeader> zoom_headers;
    TotalSummary total_summary;
    ChrTreeHeader chr_tree_header;
    std::vector<ChrTreeLeaf> chr_tree;
    std::map<std::string, ChrTreeLeaf> chr_map;

    BigwigReader(const std::string& p, uint64_t pa = 0) : path(p), parallel(pa) {
        file = std::make_shared<BufferedFile>(open_file(path, "r"));
        if (parallel == 0) parallel = get_available_threads() * 2;
    }

    std::future<void> read_headers() {
        return std::async(std::launch::async, [this]() {
            main_header = read_main_header(*file);
            zoom_headers = read_zoom_headers(*file, main_header.zoom_levels);
            total_summary = read_total_summary(*file, main_header.total_summary_offset);
            chr_tree_header = read_chr_tree_header(*file, main_header.chr_tree_offset);
            chr_tree = read_chr_tree(*file, main_header.chr_tree_offset + 32, chr_tree_header.key_size);
            chr_map = convert_chr_tree_to_map(chr_tree);
        });
    }

    int32_t select_zoom_level(uint32_t resolution) {
        int32_t best_level = -1;
        uint32_t best_reduction = 0;
        resolution /= 2;
        for (uint16_t i = 0; i < zoom_headers.size(); ++i) {
            uint32_t reduction = zoom_headers[i].reduction_level;
            if (reduction <= resolution && reduction > best_reduction) {
                best_reduction = reduction;
                best_level = i;
            }
        }
        return best_level;
    }

    ChrTreeLeaf get_chr_entry(const std::string& chr_id) {
        std::string chr_key = chr_id.substr(0, chr_tree_header.key_size);
        auto it = chr_map.find(chr_key);
        if (it == chr_map.end()) {
            if (chr_id.length() >= 3 && chr_id.substr(0, 3) == "chr") {
                chr_key = chr_id.substr(3).substr(0, chr_tree_header.key_size);
            } else {
                chr_key = ("chr" + chr_id).substr(0, chr_tree_header.key_size);
            }
            it = chr_map.find(chr_key);
            if (it == chr_map.end()) {
                std::string available_keys;
                for (const auto& entry : chr_map) {
                    if (!available_keys.empty()) available_keys += ", ";
                    available_keys += entry.first;
                }
                throw std::runtime_error("chr " + chr_id + " not in bigwig (" + available_keys + ")");
            }
        }
        return it->second;
    }

    std::vector<Loc> parse_locs(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        const std::vector<uint64_t>& ends,
        uint32_t span = 0,
        uint32_t resolution = 1) {

        std::vector<Loc> locs(chr_ids.size());
        uint64_t values_offset = 0;
        for (uint64_t i = 0; i < chr_ids.size(); ++i) {
            auto chr_entry = get_chr_entry(chr_ids[i]);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = starts[i];
            loc.end = span > 0 ? loc.start + span : ends[i];
            loc.input_index = i;
            loc.values_index = values_offset;
            locs[i] = loc;
            values_offset += (loc.end - loc.start) / resolution;
        }
        std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
            return std::tie(a.chr_index, a.start) < std::tie(b.chr_index, b.start);
        });
        return locs;
    }

    uint64_t get_coverage(const std::vector<Loc>& locs) {
        uint64_t coverage = 0;
        for (const auto& loc : locs) {
            coverage += (loc.end - loc.start);
        }
        return coverage;
    }

    std::vector<float> read_values(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        uint32_t span,
        uint32_t resolution,
        float default_value = 0.0f,
        bool use_zoom = true,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {
        
        auto locs = parse_locs(chr_ids, starts, {}, span, resolution);
        uint64_t bin_count = span / resolution;
        std::vector<float> values(locs.size() * bin_count, default_value);

        ProgressTracker tracker(get_coverage(locs), progress);

        int32_t zoom_level = use_zoom ? select_zoom_level(resolution) : -1;
        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator generator(*file, locs, tree_offset);

        std::deque<std::future<void>> futures;
        Semaphore parallel_semaphore(parallel);
        TreeNodeGeneratorNext result;
        while (!(result = generator.next()).done) {
            tracker.update(generator.coverage);
            auto future = std::async(std::launch::async, [this, &locs, result, resolution, &values, &parallel_semaphore, zoom_level]() {
                SemaphoreGuard guard(parallel_semaphore);
                if (zoom_level < 0) {
                    read_data_node_at_locs(
                        *file,
                        main_header.uncompress_buffer_size,
                        locs,
                        result.node,
                        result.start_loc_index,
                        result.end_loc_index,
                        resolution,
                        values
                    );
                } else {
                    read_zoom_data_node_at_locs(
                        *file,
                        main_header.uncompress_buffer_size,
                        locs,
                        result.node,
                        result.start_loc_index,
                        result.end_loc_index,
                        resolution,
                        values
                    );
                }
            });
            futures.push_back(std::move(future));
            while (!futures.empty()) {
                auto &future = futures.front();
                if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                    future.get();
                    futures.pop_front();
                } else {
                    break;
                }
            }
        }
        for (auto& future : futures) future.get();
        tracker.done();

        return values;
    }


    void to_bedgraph(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        std::vector<Loc> locs;
        if (chr_ids.empty()) chr_ids = get_map_keys(chr_map);
        for (std::string chr_id : chr_ids) {
            auto chr_entry = get_chr_entry(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }

        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator generator(*file, locs, tree_offset);

        auto output_file = open_file(output_path, "w");
        auto write_line = [&](std::string chr_id, uint32_t start, uint32_t end, float value) {
            std::string line =
                chr_id + "\t" +
                std::to_string(start) + "\t" +
                std::to_string(end) + "\t" +
                std::to_string(value) + "\n";
            output_file->write_string(line);
        };

        TreeNodeGeneratorNext result;
        while (!(result = generator.next()).done) {
            DataTreeLeaf node = result.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset);
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            if (zoom_level >= 0) {
                uint64_t record_count = node.data_size / 32;
                for (uint64_t i = 0; i < record_count; ++i) {
                    ZoomDataRecord record = read_zoom_data_record(buffer, i);
                    std::string chr_id = chr_tree[record.chr_index].key;
                    if (record.valid_count > 0) {
                        float value = record.sum_data / record.valid_count;
                        write_line(chr_id, record.chr_start, record.chr_end, value);
                    }
                }
                continue;
            }
            WigDataHeader header = read_wig_data_header(buffer);
            std::string chr_id = chr_tree[header.chr_index].key;
            if (header.type == 1) { // bedGraph
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 12);
                    uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
                    float value = buffer.read_float(24 + i * 12 + 8);
                    write_line(chr_id, start, end, value);
                }
            } else if (header.type == 2) { // variableStep
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 8);
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 8 + 4);
                    write_line(chr_id, start, end, value);
                }
            } else if (header.type == 3) { // fixedStep
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = header.chr_start + i * header.item_step;
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 4);
                    write_line(chr_id, start, end, value);
                }
            } else {
                throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
            }
        }
    }

    void to_wig(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        std::vector<Loc> locs;
        if (chr_ids.empty()) chr_ids = get_map_keys(chr_map);
        for (std::string chr_id : chr_ids) {
            auto chr_entry = get_chr_entry(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }

        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator generator(*file, locs, tree_offset);

        auto output_file = open_file(output_path, "w");
        auto write_header_line = [&](std::string chr_id, uint32_t start, int64_t span) {
            std::string line =
                "fixedStep chrom=" + chr_id +
                " start=" + std::to_string(start + 1) +
                " step=" + std::to_string(span) +
                " span=" + std::to_string(span) + "\n";
            output_file->write_string(line);
        };
        
        TreeNodeGeneratorNext result;
        while (!(result = generator.next()).done) {
            DataTreeLeaf node = result.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset);
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            int64_t span = -1;
            if (zoom_level >= 0) {
                uint64_t record_count = node.data_size / 32;
                for (uint64_t i = 0; i < record_count; ++i) {
                    ZoomDataRecord record = read_zoom_data_record(buffer, i);
                    std::string chr_id = chr_tree[record.chr_index].key;
                    if (record.valid_count > 0) {
                        float value = record.sum_data / record.valid_count;
                        if (record.chr_end - record.chr_start != span) {
                            span = record.chr_end - record.chr_start;
                            write_header_line(chr_id, record.chr_start, span);
                        }
                        output_file->write_string(std::to_string(value) + "\n");
                    }
                }
                continue;
            }
            WigDataHeader header = read_wig_data_header(buffer);
            std::string chr_id = chr_tree[header.chr_index].key;
            if (header.type == 1) { // bedGraph
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 12);
                    uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
                    float value = buffer.read_float(24 + i * 12 + 8);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else if (header.type == 2) { // variableStep
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 8);
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 8 + 4);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else if (header.type == 3) { // fixedStep
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = header.chr_start + i * header.item_step;
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 4);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else {
                throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
            }
        }
    }


};
