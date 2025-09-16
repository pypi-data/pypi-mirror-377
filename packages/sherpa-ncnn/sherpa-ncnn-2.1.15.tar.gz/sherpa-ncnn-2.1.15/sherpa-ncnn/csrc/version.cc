// sherpa-ncnn/csrc/version.cc
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-ncnn/csrc/version.h"

namespace sherpa_ncnn {

const char *GetGitDate() {
  static const char *date = "Tue Sep 16 08:01:06 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "c794e143";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "2.1.15";
  return version;
}

}  // namespace sherpa_ncnn
