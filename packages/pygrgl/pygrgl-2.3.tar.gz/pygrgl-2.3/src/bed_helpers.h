#ifndef GRG_BED_HELPERS_H
#define GRG_BED_HELPERS_H

#include <fstream>
#include <istream>
#include <limits>
#include <vector>

#include "grgl/common.h"
#include "util.h"

namespace grgl {

enum BEDSex {
    BS_UNKNOWN = 0,
    BS_MALE = 1,
    BS_FEMALE = 2,
};

struct FAMRow {
    std::string familyID;
    std::string indivID;
    std::string fatherID;
    std::string motherID;
    std::string sex;
    std::string phenotype;
};

constexpr size_t NUM_FAM_COLS = 6;

/**
 * Load FAM file.
 */
inline std::vector<FAMRow> loadFAM(const std::string& filename, const char separator = '\t') {
    std::ifstream infile(filename);
    if (!infile) {
        std::stringstream ssErr;
        ssErr << "Could not read file " << filename;
        throw grgl::BadInputFileFailure(ssErr.str().c_str());
    }
    std::string line;
    std::vector<FAMRow> result;
    while (std::getline(infile, line)) {
        auto tokens = split(line, separator);
        if (tokens.size() != NUM_FAM_COLS) {
            throw grgl::BadInputFileFailure("Invalid number of columns in FAM file");
        }
        result.push_back({std::move(tokens[0]),
                          std::move(tokens[1]),
                          std::move(tokens[2]),
                          std::move(tokens[3]),
                          std::move(tokens[4]),
                          std::move(tokens[5])});
    }
    return std::move(result);
}

inline Mutation parseBIMLine(const std::string& line, const char separator = '\t') {
    std::vector<std::string> tokens = split(line, separator);
    uint32_t position = 0;
    if (!parseExactUint32(tokens[3], position)) {
        throw BadInputFileFailure("Invalid base-pair position in BIM file");
    }
    return {position, std::move(tokens[4]), std::move(tokens[5])};
}

// BIM line layout:
//  Chromosome code (either an integer, or 'X'/'Y'/'XY'/'MT'; '0' indicates unknown) or name
//  Variant identifier
//  Position in morgans or centimorgans (safe to use dummy value of '0')
//  Base-pair coordinate (1-based; limited to 231-2)
//  Allele 1 (corresponding to clear bits in .bed; usually minor)
//  Allele 2 (corresponding to set bits in .bed; usually major)
inline Mutation readNextBIM(std::ifstream& inFile, const char separator = '\t') {
    release_assert(inFile.good());
    std::string line;
    if (std::getline(inFile, line)) {
        return parseBIMLine(line, separator);
    }
    return {};
}

inline size_t countVariantsBIM(std::ifstream& inFile, size_t& firstPos, size_t& lastPos, const char separator = '\t') {
    size_t count = 0;
    std::string prevLine;
    std::string line;
    Mutation first;
    while (std::getline(inFile, line)) {
        if (count == 0) {
            first = parseBIMLine(line, separator);
        }
        prevLine = std::move(line);
        count++;
    }
    Mutation last = parseBIMLine(prevLine, separator);
    firstPos = first.getPosition();
    lastPos = last.getPosition();
    return count;
}

inline std::vector<Mutation> getBIMMutations(std::ifstream& inFile,
                                             size_t startPosition,
                                             size_t endPosition,
                                             size_t& startVariant,
                                             const char separator = '\t') {
    startVariant = std::numeric_limits<size_t>::max();
    std::vector<Mutation> result;
    while (inFile.good()) {
        Mutation mut = readNextBIM(inFile);
        if (!mut.isEmpty() && mut.getPosition() >= startPosition && mut.getPosition() < endPosition) {
            if (startVariant == std::numeric_limits<size_t>::max()) {
                startVariant = mut.getPosition();
            }
            result.push_back(std::move(mut));
        } else if (startVariant != std::numeric_limits<size_t>::max()) {
            break;
        }
    }
    return std::move(result);
}

// "The rest of the file is a sequence of V blocks of N/4 (rounded up) bytes
// each, where V is the number of variants and N is the number of samples.
// The first block corresponds to the first marker in the .bim file, etc."
inline void
getBEDSamples(std::ifstream& inFile, const size_t numIndividuals, NodeIDList& samples, NodeIDList& missing) {
    const size_t bytes = roundUpToMultiple<size_t>(numIndividuals * 2, 8) / 8;
    std::vector<uint8_t> buffer(bytes);
    inFile.read((char*)buffer.data(), bytes);
    if (!inFile.good()) {
        throw BadInputFileFailure("Unexpected end of BED file");
    }
    for (size_t i = 0; i < bytes; i++) {
        uint8_t mask = 0x3U;
        for (size_t j = 0; j < 4; j++) {
            const size_t individual = (i * 4) + j;
            const size_t sample0 = individual * 2;
            const size_t sample1 = sample0 + 1;
            const uint8_t value = (buffer[i] & mask) >> j;
            switch (value) {
            case 0: break;
            case 1: // Missing genotype
                missing.push_back(sample0);
                missing.push_back(sample1);
                break;
            case 2: // Heterozygous
                samples.push_back(sample0);
                break;
            case 3: // Homozygous for second allele in .bim file
                samples.push_back(sample0);
                samples.push_back(sample1);
                break;
            default: abort();
            }
            mask <<= 2U;
        }
    }
}

} // namespace grgl

#endif /* GRG_BED_HELPERS_H */