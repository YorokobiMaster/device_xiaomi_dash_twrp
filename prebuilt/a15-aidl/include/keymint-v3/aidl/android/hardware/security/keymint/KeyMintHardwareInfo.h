/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 3 --hash 74a538630d5d90f732f361a2313cbb69b09eb047 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/secureclock/aidl/android.hardware.security.secureclock_interface/1/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging/android/hardware/security/keymint/KeyMintHardwareInfo.cpp.d -h out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint-V3-ndk-source/gen/staging -Nhardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3 hardware/interfaces/security/keymint/aidl/aidl_api/android.hardware.security.keymint/3/android/hardware/security/keymint/KeyMintHardwareInfo.aidl
 */
#pragma once

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <android/binder_interface_utils.h>
#include <android/binder_parcelable_utils.h>
#include <android/binder_to_string.h>
#include <aidl/android/hardware/security/keymint/SecurityLevel.h>
#ifdef BINDER_STABILITY_SUPPORT
#include <android/binder_stability.h>
#endif  // BINDER_STABILITY_SUPPORT

namespace aidl {
namespace android {
namespace hardware {
namespace security {
namespace keymint {
class KeyMintHardwareInfo {
public:
  typedef std::false_type fixed_size;
  static const char* descriptor;

  int32_t versionNumber = 0;
  ::aidl::android::hardware::security::keymint::SecurityLevel securityLevel = ::aidl::android::hardware::security::keymint::SecurityLevel::SOFTWARE;
  std::string keyMintName;
  std::string keyMintAuthorName;
  bool timestampTokenRequired = false;

  binder_status_t readFromParcel(const AParcel* parcel);
  binder_status_t writeToParcel(AParcel* parcel) const;

  inline bool operator==(const KeyMintHardwareInfo& _rhs) const {
    return std::tie(versionNumber, securityLevel, keyMintName, keyMintAuthorName, timestampTokenRequired) == std::tie(_rhs.versionNumber, _rhs.securityLevel, _rhs.keyMintName, _rhs.keyMintAuthorName, _rhs.timestampTokenRequired);
  }
  inline bool operator<(const KeyMintHardwareInfo& _rhs) const {
    return std::tie(versionNumber, securityLevel, keyMintName, keyMintAuthorName, timestampTokenRequired) < std::tie(_rhs.versionNumber, _rhs.securityLevel, _rhs.keyMintName, _rhs.keyMintAuthorName, _rhs.timestampTokenRequired);
  }
  inline bool operator!=(const KeyMintHardwareInfo& _rhs) const {
    return !(*this == _rhs);
  }
  inline bool operator>(const KeyMintHardwareInfo& _rhs) const {
    return _rhs < *this;
  }
  inline bool operator>=(const KeyMintHardwareInfo& _rhs) const {
    return !(*this < _rhs);
  }
  inline bool operator<=(const KeyMintHardwareInfo& _rhs) const {
    return !(_rhs < *this);
  }

  static const ::ndk::parcelable_stability_t _aidl_stability = ::ndk::STABILITY_VINTF;
  inline std::string toString() const {
    std::ostringstream _aidl_os;
    _aidl_os << "KeyMintHardwareInfo{";
    _aidl_os << "versionNumber: " << ::android::internal::ToString(versionNumber);
    _aidl_os << ", securityLevel: " << ::android::internal::ToString(securityLevel);
    _aidl_os << ", keyMintName: " << ::android::internal::ToString(keyMintName);
    _aidl_os << ", keyMintAuthorName: " << ::android::internal::ToString(keyMintAuthorName);
    _aidl_os << ", timestampTokenRequired: " << ::android::internal::ToString(timestampTokenRequired);
    _aidl_os << "}";
    return _aidl_os.str();
  }
};
}  // namespace keymint
}  // namespace security
}  // namespace hardware
}  // namespace android
}  // namespace aidl
