#include "../../operator.h"
#include "../../handle.h"
#include "infiniop/ops/softplus.h"

#ifdef ENABLE_CPU_API
#include "cpu/softplus_cpu.h"
#endif
#if defined(ENABLE_NVIDIA_API) || defined(ENABLE_ILUVATAR_API)
#include "nvidia/softplus_nvidia.cuh"
#endif
#ifdef ENABLE_METAX_API
#include "metax/softplus_metax.h"
#endif

__C infiniStatus_t infiniopCreateSoftplusDescriptor(
    infiniopHandle_t handle,
    infiniopSoftplusDescriptor_t *desc_ptr,
    infiniopTensorDescriptor_t y_desc,
    infiniopTensorDescriptor_t x_desc) {

#define CREATE(CASE, NAMESPACE)                                                 \
    case CASE:                                                                  \
        return op::softplus::NAMESPACE::Descriptor::create(                     \
            handle,                                                             \
            reinterpret_cast<op::softplus::NAMESPACE::Descriptor **>(desc_ptr), \
            y_desc,                                                             \
            {x_desc})

    switch (handle->device) {

#ifdef ENABLE_CPU_API
        CREATE(INFINI_DEVICE_CPU, cpu);
#endif
#ifdef ENABLE_NVIDIA_API
        CREATE(INFINI_DEVICE_NVIDIA, nvidia);
#endif
#ifdef ENABLE_ILUVATAR_API
        CREATE(INFINI_DEVICE_ILUVATAR, nvidia);
#endif

    default:
        return INFINI_STATUS_DEVICE_TYPE_NOT_SUPPORTED;
    }

#undef CREATE
}

__C infiniStatus_t infiniopGetSoftplusWorkspaceSize(infiniopSoftplusDescriptor_t desc, size_t *size) {

#define GET(CASE, NAMESPACE)                                                                    \
    case CASE:                                                                                  \
        *size = reinterpret_cast<op::softplus::NAMESPACE::Descriptor *>(desc)->workspaceSize(); \
        return INFINI_STATUS_SUCCESS

    switch (desc->device_type) {
#ifdef ENABLE_CPU_API
        GET(INFINI_DEVICE_CPU, cpu);
#endif
#ifdef ENABLE_NVIDIA_API
        GET(INFINI_DEVICE_NVIDIA, nvidia);
#endif
#ifdef ENABLE_ILUVATAR_API
        GET(INFINI_DEVICE_ILUVATAR, nvidia);
#endif

    default:
        return INFINI_STATUS_DEVICE_TYPE_NOT_SUPPORTED;
    }
#undef GET

    return INFINI_STATUS_DEVICE_TYPE_NOT_SUPPORTED;
}

__C infiniStatus_t infiniopSoftplus(
    infiniopSoftplusDescriptor_t desc,
    void *workspace,
    size_t workspace_size,
    void *y,
    const void *x,
    void *stream) {

#define CALCULATE(CASE, NAMESPACE)                                                 \
    case CASE:                                                                     \
        return reinterpret_cast<const op::softplus::NAMESPACE::Descriptor *>(desc) \
            ->calculate(workspace, workspace_size, y, {x}, stream)

    switch (desc->device_type) {

#ifdef ENABLE_CPU_API
        CALCULATE(INFINI_DEVICE_CPU, cpu);
#endif
#ifdef ENABLE_NVIDIA_API
        CALCULATE(INFINI_DEVICE_NVIDIA, nvidia);
#endif
#ifdef ENABLE_ILUVATAR_API
        CALCULATE(INFINI_DEVICE_ILUVATAR, nvidia);
#endif

    default:
        return INFINI_STATUS_DEVICE_TYPE_NOT_SUPPORTED;
    }

#undef CALCULATE
}

__C infiniStatus_t
infiniopDestroySoftplusDescriptor(infiniopSoftplusDescriptor_t desc) {

#define DELETE(CASE, NAMESPACE)                                                     \
    case CASE:                                                                      \
        delete reinterpret_cast<const op::softplus::NAMESPACE::Descriptor *>(desc); \
        return INFINI_STATUS_SUCCESS

    switch (desc->device_type) {

#ifdef ENABLE_CPU_API
        DELETE(INFINI_DEVICE_CPU, cpu);
#endif
#ifdef ENABLE_NVIDIA_API
        DELETE(INFINI_DEVICE_NVIDIA, nvidia);
#endif
#ifdef ENABLE_ILUVATAR_API
        DELETE(INFINI_DEVICE_ILUVATAR, nvidia);
#endif

    default:
        return INFINI_STATUS_DEVICE_TYPE_NOT_SUPPORTED;
    }

#undef DELETE
}
