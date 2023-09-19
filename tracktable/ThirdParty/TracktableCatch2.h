/*
 * Copyright (c) 2014-2023 National Technology and Engineering
 * Solutions of Sandia, LLC. Under the terms of Contract DE-NA0003525
 * with National Technology and Engineering Solutions of Sandia, LLC,
 * the U.S. Government retains certain rights in this software.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


// Catch2 is a header-only test framework that we are starting to use for
// test cases.
//
// Include this file at the top of your test case.  Mike S. is going to
// teach us soon how to write test cases using Catch2.

//Listener source https://github.com/catchorg/Catch2/blob/devel/examples/210-Evt-EventListeners.cpp

#ifndef __tracktable_Catch2_h
#define __tracktable_Catch2_h

#define CATCH_CONFIG_MAIN
#include <tracktable/ThirdParty/catch2.hpp>
#include <iostream>

namespace {
    std::ostream& stream = std::cerr;

    std::string ws(int const level) {
        return std::string(2 * level, ' ');
    }

    template< typename T >
    std::ostream& operator<<( std::ostream& os, std::vector<T> const& v ) {
        os << "{ ";
        for ( const auto& x : v )
            os << x << ", ";
        return os << "}";
    }
    // struct SourceLineInfo {
    //     char const* file;
    //     std::size_t line;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::SourceLineInfo const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- file: " << info.file << "\n"
           << ws(level+1) << "- line: " << info.line << "\n";
    }

    //struct MessageInfo {
    //    std::string macroName;
    //    std::string message;
    //    SourceLineInfo lineInfo;
    //    ResultWas::OfType type;
    //    unsigned int sequence;
    //};

    void print( std::ostream& os, int const level, Catch::MessageInfo const& info ) {
        os << ws(level+1) << "- macroName: '" << info.macroName << "'\n"
           << ws(level+1) << "- message '"    << info.message   << "'\n";
        print( os,level+1  , "- lineInfo", info.lineInfo );
        os << ws(level+1) << "- sequence "    << info.sequence  << "\n";
    }

    void print( std::ostream& os, int const level, std::string const& title, std::vector<Catch::MessageInfo> const& v ) {
        os << ws(level  ) << title << ":\n";
        for ( const auto& x : v )
        {
            os << ws(level+1) << "{\n";
            print( os, level+2, x );
            os << ws(level+1) << "}\n";
        }
    //    os << ws(level+1) << "\n";
    }

    // struct TestRunInfo {
    //     std::string name;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::TestRunInfo const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- name: " << info.name << "\n";
    }

    // struct Counts {
    //     std::size_t total() const;
    //     bool allPassed() const;
    //     bool allOk() const;
    //
    //     std::size_t passed = 0;
    //     std::size_t failed = 0;
    //     std::size_t failedButOk = 0;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::Counts const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- total(): "     << info.total()     << "\n"
           << ws(level+1) << "- allPassed(): " << info.allPassed() << "\n"
           << ws(level+1) << "- allOk(): "     << info.allOk()     << "\n"
           << ws(level+1) << "- passed: "      << info.passed      << "\n"
           << ws(level+1) << "- failed: "      << info.failed      << "\n"
           << ws(level+1) << "- failedButOk: " << info.failedButOk << "\n";
    }

    // struct Totals {
    //     Counts assertions;
    //     Counts testCases;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::Totals const& info ) {
        os << ws(level) << title << ":\n";
        print( os, level+1, "- assertions", info.assertions );
        print( os, level+1, "- testCases" , info.testCases  );
    }

    // struct TestRunStats {
    //     TestRunInfo runInfo;
    //     Totals totals;
    //     bool aborting;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::TestRunStats const& info ) {
        os << ws(level) << title << ":\n";
        print( os, level+1 , "- runInfo", info.runInfo );
        print( os, level+1 , "- totals" , info.totals  );
        os << ws(level+1) << "- aborting: " << info.aborting << "\n";
    }

    //    struct Tag {
    //        StringRef original, lowerCased;
    //    };
    //
    //
    //    enum class TestCaseProperties : uint8_t {
    //        None = 0,
    //        IsHidden = 1 << 1,
    //        ShouldFail = 1 << 2,
    //        MayFail = 1 << 3,
    //        Throws = 1 << 4,
    //        NonPortable = 1 << 5,
    //        Benchmark = 1 << 6
    //    };
    //
    //
    //    struct TestCaseInfo : NonCopyable {
    //
    //        bool isHidden() const;
    //        bool throws() const;
    //        bool okToFail() const;
    //        bool expectedToFail() const;
    //
    //
    //        std::string name;
    //        std::string className;
    //        std::vector<Tag> tags;
    //        SourceLineInfo lineInfo;
    //        TestCaseProperties properties = TestCaseProperties::None;
    //    };

    void print( std::ostream& os, int const level, std::string const& title, Catch::TestCaseInfo const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- isHidden(): "       << info.isHidden() << "\n"
           << ws(level+1) << "- throws(): "         << info.throws() << "\n"
           << ws(level+1) << "- okToFail(): "       << info.okToFail() << "\n"
           << ws(level+1) << "- expectedToFail(): " << info.expectedToFail() << "\n"
           << ws(level+1) << "- tagsAsString(): '"  << info.tagsAsString() << "'\n"
           << ws(level+1) << "- name: '"            << info.name << "'\n"
           << ws(level+1) << "- className: '"       << info.className << "'\n"
           << ws(level+1) << "- tags: "             << info.tags << "\n";
        print( os, level+1 , "- lineInfo", info.lineInfo );
        os << ws(level+1) << "- properties (flags): 0x" << std::hex << static_cast<uint32_t>(info.properties) << std::dec << "\n";
    }

    // struct TestCaseStats {
    //     TestCaseInfo testInfo;
    //     Totals totals;
    //     std::string stdOut;
    //     std::string stdErr;
    //     bool aborting;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::TestCaseStats const& info ) {
        os << ws(level  ) << title << ":\n";
        print( os, level+1 , "- testInfo", info.testInfo );
        print( os, level+1 , "- totals"  , info.totals   );
        os << ws(level+1) << "- stdOut: "   << info.stdOut << "\n"
           << ws(level+1) << "- stdErr: "   << info.stdErr << "\n"
           << ws(level+1) << "- aborting: " << info.aborting << "\n";
    }

    // struct SectionInfo {
    //     std::string name;
    //     std::string description;
    //     SourceLineInfo lineInfo;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::SectionInfo const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- name: "         << info.name << "\n";
        print( os, level+1 , "- lineInfo", info.lineInfo );
    }

    // struct SectionStats {
    //     SectionInfo sectionInfo;
    //     Counts assertions;
    //     double durationInSeconds;
    //     bool missingAssertions;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::SectionStats const& info ) {
        os << ws(level  ) << title << ":\n";
        print( os, level+1 , "- sectionInfo", info.sectionInfo );
        print( os, level+1 , "- assertions" , info.assertions );
        os << ws(level+1) << "- durationInSeconds: " << info.durationInSeconds << "\n"
           << ws(level+1) << "- missingAssertions: " << info.missingAssertions << "\n";
    }

    // struct AssertionInfo
    // {
    //     StringRef macroName;
    //     SourceLineInfo lineInfo;
    //     StringRef capturedExpression;
    //     ResultDisposition::Flags resultDisposition;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::AssertionInfo const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- macroName: '"  << info.macroName << "'\n";
        print( os, level+1 , "- lineInfo" , info.lineInfo );
        os << ws(level+1) << "- capturedExpression: '" << info.capturedExpression << "'\n"
           << ws(level+1) << "- resultDisposition (flags): 0x" << std::hex << info.resultDisposition  << std::dec << "\n";
    }

    //struct AssertionResultData
    //{
    //    std::string reconstructExpression() const;
    //
    //    std::string message;
    //    mutable std::string reconstructedExpression;
    //    LazyExpression lazyExpression;
    //    ResultWas::OfType resultType;
    //};

    void print( std::ostream& os, int const level, std::string const& title, Catch::AssertionResultData const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- reconstructExpression(): '" <<   info.reconstructExpression() << "'\n"
           << ws(level+1) << "- message: '"                 <<   info.message << "'\n"
           << ws(level+1) << "- lazyExpression: '"          << "(info.lazyExpression)" << "'\n"
           << ws(level+1) << "- resultType: '"              <<   info.resultType << "'\n";
    }

    //class AssertionResult {
    //    bool isOk() const;
    //    bool succeeded() const;
    //    ResultWas::OfType getResultType() const;
    //    bool hasExpression() const;
    //    bool hasMessage() const;
    //    std::string getExpression() const;
    //    std::string getExpressionInMacro() const;
    //    bool hasExpandedExpression() const;
    //    std::string getExpandedExpression() const;
    //    std::string getMessage() const;
    //    SourceLineInfo getSourceInfo() const;
    //    std::string getTestMacroName() const;
    //
    //    AssertionInfo m_info;
    //    AssertionResultData m_resultData;
    //};

    void print( std::ostream& os, int const level, std::string const& title, Catch::AssertionResult const& info ) {
        os << ws(level  ) << title << ":\n"
           << ws(level+1) << "- isOk(): "  << info.isOk() << "\n"
           << ws(level+1) << "- succeeded(): "  << info.succeeded() << "\n"
           << ws(level+1) << "- getResultType(): "  << info.getResultType() << "\n"
           << ws(level+1) << "- hasExpression(): "  << info.hasExpression() << "\n"
           << ws(level+1) << "- hasMessage(): "  << info.hasMessage() << "\n"
           << ws(level+1) << "- getExpression(): '"  << info.getExpression() << "'\n"
           << ws(level+1) << "- getExpressionInMacro(): '"  << info.getExpressionInMacro()  << "'\n"
           << ws(level+1) << "- hasExpandedExpression(): "  << info.hasExpandedExpression() << "\n"
           << ws(level+1) << "- getExpandedExpression(): "  << info.getExpandedExpression() << "'\n"
           << ws(level+1) << "- getMessage(): '"  << info.getMessage() << "'\n";
        print( os, level+1 , "- getSourceInfo(): ", info.getSourceInfo() );
        os << ws(level+1) << "- getTestMacroName(): '"  << info.getTestMacroName() << "'\n";

        print( os, level+1 , "- *** m_info (AssertionInfo)", info.m_info );
        print( os, level+1 , "- *** m_resultData (AssertionResultData)", info.m_resultData );
    }

    // struct AssertionStats {
    //     AssertionResult assertionResult;
    //     std::vector<MessageInfo> infoMessages;
    //     Totals totals;
    // };

    void print( std::ostream& os, int const level, std::string const& title, Catch::AssertionStats const& info ) {
        os << ws(level  ) << title << ":\n";
        print( os, level+1 , "- assertionResult", info.assertionResult );
        print( os, level+1 , "- infoMessages", info.infoMessages );
        print( os, level+1 , "- totals", info.totals );
    }

    void printSummaryRow(std::string const& label, std::vector<Catch::SummaryColumn> const& cols, std::size_t row) {
        for (auto col : cols) {
            std::string value = col.rows[row];
            if (col.label.empty()) {
                stream << label << ": ";
                if (value != "0")
                    stream << value;
                else
                    stream << Catch::Colour(Catch::Colour::Warning) << "- none -";
            }
            else if (value != "0") {
                stream << Catch::Colour(Catch::Colour::LightGrey) << " | ";
                stream << Catch::Colour(col.colour)
                    << value << ' ' << col.label;
            }
        }
        stream << '\n';
    }

    void printTotals(Catch::Totals const& totals) {
        if (totals.testCases.total() == 0) {
            stream << Catch::Colour(Catch::Colour::Warning) << "No tests ran\n";
        }
        else if (totals.assertions.total() > 0 && totals.testCases.allPassed()) {
            stream << Catch::Colour(Catch::Colour::ResultSuccess) << "All tests passed";
            stream << " ("
                << Catch::pluralise(totals.assertions.passed, "assertion") << " in "
                << Catch::pluralise(totals.testCases.passed, "test case") << ')'
                << '\n';
        }
        else {

            std::vector<Catch::SummaryColumn> columns;
            columns.push_back(Catch::SummaryColumn("", Catch::Colour::None)
                .addRow(totals.testCases.total())
                .addRow(totals.assertions.total()));
            columns.push_back(Catch::SummaryColumn("passed", Catch::Colour::Success)
                .addRow(totals.testCases.passed)
                .addRow(totals.assertions.passed));
            columns.push_back(Catch::SummaryColumn("failed", Catch::Colour::ResultError)
                .addRow(totals.testCases.failed)
                .addRow(totals.assertions.failed));
            columns.push_back(Catch::SummaryColumn("failed as expected", Catch::Colour::ResultExpectedFailure)
                .addRow(totals.testCases.failedButOk)
                .addRow(totals.assertions.failedButOk));

            printSummaryRow("test cases", columns, 0);
            printSummaryRow("assertions", columns, 1);
        }
    }

    void printTotalsDivider(Catch::Totals const& totals) {
        if (totals.testCases.total() > 0) {
            std::size_t failedRatio = Catch::makeRatio(totals.testCases.failed, totals.testCases.total());
            std::size_t failedButOkRatio = Catch::makeRatio(totals.testCases.failedButOk, totals.testCases.total());
            std::size_t passedRatio = Catch::makeRatio(totals.testCases.passed, totals.testCases.total());
            while (failedRatio + failedButOkRatio + passedRatio < CATCH_CONFIG_CONSOLE_WIDTH - 1)
                Catch::findMax(failedRatio, failedButOkRatio, passedRatio)++;
            while (failedRatio + failedButOkRatio + passedRatio > CATCH_CONFIG_CONSOLE_WIDTH - 1)
                Catch::findMax(failedRatio, failedButOkRatio, passedRatio)--;

            stream << Catch::Colour(Catch::Colour::Error) << std::string(failedRatio, '=');
            stream << Catch::Colour(Catch::Colour::ResultExpectedFailure) << std::string(failedButOkRatio, '=');
            if (totals.testCases.allPassed())
                stream << Catch::Colour(Catch::Colour::ResultSuccess) << std::string(passedRatio, '=');
            else
                stream << Catch::Colour(Catch::Colour::Success) << std::string(passedRatio, '=');
        }
        else {
            stream << Catch::Colour(Catch::Colour::Warning) << std::string(CATCH_CONFIG_CONSOLE_WIDTH - 1, '=');
        }
        stream << '\n';
    }

    char const * dashed_line =
    "--------------------------------------------------------------------------";
    struct MyListener : Catch::TestEventListenerBase {

        using TestEventListenerBase::TestEventListenerBase; // inherit constructor

        void testRunEnded(Catch::TestRunStats const& testRunStats) override {
            printTotalsDivider(testRunStats.totals);
            printTotals(testRunStats.totals);
        }

        // Sections ending
        void sectionEnded(Catch::SectionStats const& sectionStats) override {
            //std::cout << "\nEvent: sectionEnded:\n";
            //print(std::cout, 1, "- sectionStats", sectionStats);
        }

        bool assertionEnded(Catch::AssertionStats const& assertionStats) override {

            if (!assertionStats.assertionResult.isOk()) {
                std::cout << std::endl << dashed_line << std::endl << std::endl;
                std::cout << assertionStats.assertionResult.getSourceInfo().file << " ("
                    << assertionStats.assertionResult.getSourceInfo().line << "): FAILED:\n";
                if(assertionStats.assertionResult.hasExpression())
                    std::cout << "\t" << assertionStats.assertionResult.getExpressionInMacro() << "\n";
                if(assertionStats.assertionResult.hasExpandedExpression())
                    std::cout << "with expansion:\n"
                        << "\t" << assertionStats.assertionResult.getExpandedExpression() << "\n";
                std::cout << std::endl << dashed_line << std::endl;
            }
            return true;
        }

        // Test cases ending
        void testCaseEnded(Catch::TestCaseStats const& testCaseStats) override {
            //std::cout << "\nEvent: testCaseEnded:\n";
            //print(std::cout, 1, "testCaseStats", testCaseStats);
        }

    };
}
CATCH_REGISTER_LISTENER( MyListener )


#endif