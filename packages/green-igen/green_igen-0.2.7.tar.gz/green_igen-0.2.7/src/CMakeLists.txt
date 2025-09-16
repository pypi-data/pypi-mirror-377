# Copyright 2014-2018 The PySCF Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

configure_file(
  "${PROJECT_SOURCE_DIR}/src/config.h.in"
  "${PROJECT_BINARY_DIR}/src/config.h")

add_library(pbc0 SHARED ft_ao.c fill_ints.c optimizer.c grid_ao.c nr_direct.c
                fill_int2c.c fill_nr_3c.c fill_r_3c.c fill_int2e.c fill_r_4c.c
  ft_ao.c ft_ao_deriv.c fill_grids_int2c.c
  grid_ao_drv.c deriv1.c deriv2.c nr_ecp.c nr_ecp_deriv.c
  autocode/auto_eval1.c fill_nr_s8.c nr_incore.c nr_direct.c optimizer.c nr_direct_dot.c
  time_rev.c r_direct_o1.c rkb_screen.c
  r_direct_dot.c rah_direct_dot.c rha_direct_dot.c
  hessian_screen.c nr_sgx_direct.c transpose.c pack_tril.c npdot.c condense.c omp_reduce.c np_helper.c
  $<TARGET_OBJECTS:cint>
  )

target_include_directories(pbc0 PUBLIC "${PROJECT_SOURCE_DIR}/src")
target_include_directories(pbc0 PUBLIC "${PROJECT_SOURCE_DIR}/src/green/igen")
target_include_directories(pbc0 PUBLIC "${PROJECT_BINARY_DIR}/src")
target_include_directories(pbc0 PUBLIC "${PROJECT_BINARY_DIR}/deps/include")

set_target_properties(pbc0 PROPERTIES
  COMPILE_FLAGS ${OpenMP_C_FLAGS}
  LINK_FLAGS ${OpenMP_C_FLAGS})

target_link_libraries(pbc0 PUBLIC ${BLAS_LIBRARIES} m)
if (HAVE_LIBQUADMATH AND HAVE_QUADMATH_H)
    target_link_libraries(pbc0 PUBLIC quadmath)
    target_compile_definitions(pbc0 PUBLIC USE_LIBQUADMATH)
endif()
