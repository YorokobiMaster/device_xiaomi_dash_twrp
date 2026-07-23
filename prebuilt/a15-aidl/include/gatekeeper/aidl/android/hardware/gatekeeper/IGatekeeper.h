/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 1 --hash d877e8a1608a00fd9068bcd7e69ea480a7ea17f0 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint_interface/3/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging/android/hardware/gatekeeper/IGatekeeper.cpp.d -h out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging -Nhardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1 hardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1/android/hardware/gatekeeper/IGatekeeper.aidl
 */
#pragma once

#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <android/binder_ibinder_platform.h>
#include <android/binder_interface_utils.h>
#include <android/binder_parcel_platform.h>
#include <aidl/android/hardware/gatekeeper/GatekeeperEnrollResponse.h>
#include <aidl/android/hardware/gatekeeper/GatekeeperVerifyResponse.h>
#ifdef BINDER_STABILITY_SUPPORT
#include <android/binder_stability.h>
#endif  // BINDER_STABILITY_SUPPORT

namespace aidl::android::hardware::gatekeeper {
class GatekeeperEnrollResponse;
class GatekeeperVerifyResponse;
}  // namespace aidl::android::hardware::gatekeeper
namespace aidl {
namespace android {
namespace hardware {
namespace gatekeeper {
class IGatekeeperDelegator;

class IGatekeeper : public ::ndk::ICInterface {
public:
  typedef IGatekeeperDelegator DefaultDelegator;
  static const char* descriptor;
  IGatekeeper();
  virtual ~IGatekeeper();

  enum : int32_t { STATUS_REENROLL = 1 };
  enum : int32_t { STATUS_OK = 0 };
  enum : int32_t { ERROR_GENERAL_FAILURE = -1 };
  enum : int32_t { ERROR_RETRY_TIMEOUT = -2 };
  enum : int32_t { ERROR_NOT_IMPLEMENTED = -3 };
  static inline const int32_t version = 1;
  static inline const std::string hash = "d877e8a1608a00fd9068bcd7e69ea480a7ea17f0";
  static constexpr uint32_t TRANSACTION_deleteAllUsers = FIRST_CALL_TRANSACTION + 0;
  static constexpr uint32_t TRANSACTION_deleteUser = FIRST_CALL_TRANSACTION + 1;
  static constexpr uint32_t TRANSACTION_enroll = FIRST_CALL_TRANSACTION + 2;
  static constexpr uint32_t TRANSACTION_verify = FIRST_CALL_TRANSACTION + 3;

  static std::shared_ptr<IGatekeeper> fromBinder(const ::ndk::SpAIBinder& binder);
  static binder_status_t writeToParcel(AParcel* parcel, const std::shared_ptr<IGatekeeper>& instance);
  static binder_status_t readFromParcel(const AParcel* parcel, std::shared_ptr<IGatekeeper>* instance);
  static bool setDefaultImpl(const std::shared_ptr<IGatekeeper>& impl);
  static const std::shared_ptr<IGatekeeper>& getDefaultImpl();
  virtual ::ndk::ScopedAStatus deleteAllUsers() = 0;
  virtual ::ndk::ScopedAStatus deleteUser(int32_t in_uid) = 0;
  virtual ::ndk::ScopedAStatus enroll(int32_t in_uid, const std::vector<uint8_t>& in_currentPasswordHandle, const std::vector<uint8_t>& in_currentPassword, const std::vector<uint8_t>& in_desiredPassword, ::aidl::android::hardware::gatekeeper::GatekeeperEnrollResponse* _aidl_return) = 0;
  virtual ::ndk::ScopedAStatus verify(int32_t in_uid, int64_t in_challenge, const std::vector<uint8_t>& in_enrolledPasswordHandle, const std::vector<uint8_t>& in_providedPassword, ::aidl::android::hardware::gatekeeper::GatekeeperVerifyResponse* _aidl_return) = 0;
  virtual ::ndk::ScopedAStatus getInterfaceVersion(int32_t* _aidl_return) = 0;
  virtual ::ndk::ScopedAStatus getInterfaceHash(std::string* _aidl_return) = 0;
private:
  static std::shared_ptr<IGatekeeper> default_impl;
};
class IGatekeeperDefault : public IGatekeeper {
public:
  ::ndk::ScopedAStatus deleteAllUsers() override;
  ::ndk::ScopedAStatus deleteUser(int32_t in_uid) override;
  ::ndk::ScopedAStatus enroll(int32_t in_uid, const std::vector<uint8_t>& in_currentPasswordHandle, const std::vector<uint8_t>& in_currentPassword, const std::vector<uint8_t>& in_desiredPassword, ::aidl::android::hardware::gatekeeper::GatekeeperEnrollResponse* _aidl_return) override;
  ::ndk::ScopedAStatus verify(int32_t in_uid, int64_t in_challenge, const std::vector<uint8_t>& in_enrolledPasswordHandle, const std::vector<uint8_t>& in_providedPassword, ::aidl::android::hardware::gatekeeper::GatekeeperVerifyResponse* _aidl_return) override;
  ::ndk::ScopedAStatus getInterfaceVersion(int32_t* _aidl_return) override;
  ::ndk::ScopedAStatus getInterfaceHash(std::string* _aidl_return) override;
  ::ndk::SpAIBinder asBinder() override;
  bool isRemote() override;
};
}  // namespace gatekeeper
}  // namespace hardware
}  // namespace android
}  // namespace aidl
