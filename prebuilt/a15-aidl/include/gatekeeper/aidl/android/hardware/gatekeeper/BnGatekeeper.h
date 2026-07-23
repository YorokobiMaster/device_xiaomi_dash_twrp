/*
 * This file is auto-generated.  DO NOT MODIFY.
 * Using: out/host/linux-x86/bin/aidl --lang=ndk --structured --version 1 --hash d877e8a1608a00fd9068bcd7e69ea480a7ea17f0 --stability vintf --min_sdk_version current -pout/soong/.intermediates/hardware/interfaces/security/keymint/aidl/android.hardware.security.keymint_interface/3/preprocessed.aidl --ninja -d out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging/android/hardware/gatekeeper/IGatekeeper.cpp.d -h out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/include/staging -o out/soong/.intermediates/hardware/interfaces/gatekeeper/aidl/android.hardware.gatekeeper-V1-ndk-source/gen/staging -Nhardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1 hardware/interfaces/gatekeeper/aidl/aidl_api/android.hardware.gatekeeper/1/android/hardware/gatekeeper/IGatekeeper.aidl
 */
#pragma once

#include "aidl/android/hardware/gatekeeper/IGatekeeper.h"

#include <android/binder_ibinder.h>
#include <cassert>

#ifndef __BIONIC__
#ifndef __assert2
#define __assert2(a,b,c,d) ((void)0)
#endif
#endif

namespace aidl {
namespace android {
namespace hardware {
namespace gatekeeper {
class BnGatekeeper : public ::ndk::BnCInterface<IGatekeeper> {
public:
  BnGatekeeper();
  virtual ~BnGatekeeper();
  ::ndk::ScopedAStatus getInterfaceVersion(int32_t* _aidl_return) final;
  ::ndk::ScopedAStatus getInterfaceHash(std::string* _aidl_return) final;
protected:
  ::ndk::SpAIBinder createBinder() override;
private:
};
class IGatekeeperDelegator : public BnGatekeeper {
public:
  explicit IGatekeeperDelegator(const std::shared_ptr<IGatekeeper> &impl) : _impl(impl) {
     int32_t _impl_ver = 0;
     if (!impl->getInterfaceVersion(&_impl_ver).isOk()) {;
        __assert2(__FILE__, __LINE__, __PRETTY_FUNCTION__, "Delegator failed to get version of the implementation.");
     }
     if (_impl_ver != IGatekeeper::version) {
        __assert2(__FILE__, __LINE__, __PRETTY_FUNCTION__, "Mismatched versions of delegator and implementation is not allowed.");
     }
  }

  ::ndk::ScopedAStatus deleteAllUsers() override {
    return _impl->deleteAllUsers();
  }
  ::ndk::ScopedAStatus deleteUser(int32_t in_uid) override {
    return _impl->deleteUser(in_uid);
  }
  ::ndk::ScopedAStatus enroll(int32_t in_uid, const std::vector<uint8_t>& in_currentPasswordHandle, const std::vector<uint8_t>& in_currentPassword, const std::vector<uint8_t>& in_desiredPassword, ::aidl::android::hardware::gatekeeper::GatekeeperEnrollResponse* _aidl_return) override {
    return _impl->enroll(in_uid, in_currentPasswordHandle, in_currentPassword, in_desiredPassword, _aidl_return);
  }
  ::ndk::ScopedAStatus verify(int32_t in_uid, int64_t in_challenge, const std::vector<uint8_t>& in_enrolledPasswordHandle, const std::vector<uint8_t>& in_providedPassword, ::aidl::android::hardware::gatekeeper::GatekeeperVerifyResponse* _aidl_return) override {
    return _impl->verify(in_uid, in_challenge, in_enrolledPasswordHandle, in_providedPassword, _aidl_return);
  }
protected:
private:
  std::shared_ptr<IGatekeeper> _impl;
};

}  // namespace gatekeeper
}  // namespace hardware
}  // namespace android
}  // namespace aidl
