/* Copyright 2014-2018 The PySCF Developers. All Rights Reserved.
  
   Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
 
        http://www.apache.org/licenses/LICENSE-2.0
 
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

 *
 * Author: Qiming Sun <osirpt.sun@gmail.com>
 */

#include <stdlib.h>
#include <assert.h>
#include <math.h>
//#include <omp.h>
#include "config.h"
#include "cint.h"
#include "optimizer.h"
#include "nr_direct.h"
#include "np_helper.h"
#include "gto.h"

#define AO_BLOCK_SIZE   32

#define DECLARE_ALL \
        const int *atm = envs->atm; \
        const int *bas = envs->bas; \
        const double *env = envs->env; \
        const int natm = envs->natm; \
        const int nbas = envs->nbas; \
        const int *ao_loc = envs->ao_loc; \
        const int *shls_slice = envs->shls_slice; \
        const CINTOpt *cintopt = envs->cintopt; \
        const int ioff = ao_loc[shls_slice[0]]; \
        const int joff = ao_loc[shls_slice[2]]; \
        const int koff = ao_loc[shls_slice[4]]; \
        const int loff = ao_loc[shls_slice[6]]; \
        const int ish0 = ishls[0]; \
        const int ish1 = ishls[1]; \
        const int jsh0 = jshls[0]; \
        const int jsh1 = jshls[1]; \
        const int ksh0 = kshls[0]; \
        const int ksh1 = kshls[1]; \
        const int lsh0 = lshls[0]; \
        const int lsh1 = lshls[1]; \
        int shls[4]; \
        void (*pf)(double *eri, double *dm, JKArray *vjk, int *shls, \
                   int i0, int i1, int j0, int j1, \
                   int k0, int k1, int l0, int l1); \
        int (*fprescreen)(); \
        if (vhfopt) { \
                fprescreen = vhfopt->fprescreen; \
        } else { \
                fprescreen = CVHFnoscreen; \
        } \
        int ish, jsh, ksh, lsh, i0, j0, k0, l0, i1, j1, k1, l1, idm;

#define INTOR_AND_CONTRACT \
        shls[0] = ish; \
        shls[1] = jsh; \
        shls[2] = ksh; \
        shls[3] = lsh; \
        if ((*fprescreen)(shls, vhfopt, atm, bas, env) \
            && (*intor)(buf, NULL, shls, atm, natm, bas, nbas, env, \
                        cintopt, cache)) { \
                i0 = ao_loc[ish] - ioff; \
                j0 = ao_loc[jsh] - joff; \
                k0 = ao_loc[ksh] - koff; \
                l0 = ao_loc[lsh] - loff; \
                i1 = ao_loc[ish+1] - ioff; \
                j1 = ao_loc[jsh+1] - joff; \
                k1 = ao_loc[ksh+1] - koff; \
                l1 = ao_loc[lsh+1] - loff; \
                for (idm = 0; idm < n_dm; idm++) { \
                        pf = jkop[idm]->contract; \
                        (*pf)(buf, dms[idm], vjk[idm], shls, \
                              i0, i1, j0, j1, k0, k1, l0, l1); \
                } \
        }



#include <stdlib.h>
#include <assert.h>
#include <math.h>
//#include <omp.h>
#include "config.h"
#include "cint.h"
#include "cint_funcs.h"
#include "nr_direct.h"

#define MIN(I,J)        ((I) < (J) ? (I) : (J))
#define MAX(I,J)        ((I) > (J) ? (I) : (J))

int GTOmax_shell_dim(const int *ao_loc, const int *shls_slice, int ncenter);

static int _max_cache_size(int (*intor)(), int *shls_slice, int *images_loc,
                           int *atm, int natm, int *bas, int nbas, double *env)
{
        int i, n;
        int i0 = shls_slice[0];
        int i1 = shls_slice[1];
        int shls[4];
        int cache_size = 0;
        for (i = i0; i < i1; i++) {
                shls[0] = images_loc[i];
                shls[1] = images_loc[i];
                shls[2] = images_loc[i];
                shls[3] = images_loc[i];
                n = (*intor)(NULL, NULL, shls, atm, natm, bas, nbas, env, NULL, NULL);
                cache_size = MAX(cache_size, n);
        }
        return cache_size;
}

static int _assemble_eris(double *eri_buf, int *images_loc,
                          int ishell, int jshell, int kshell, int lshell,
                          double cutoff, CVHFOpt *vhfopt, IntorEnvs *envs)
{
        int *atm = envs->atm;
        int *bas = envs->bas;
        double *env = envs->env;
        int natm = envs->natm;
        int nbas = envs->nbas;
        CINTOpt *cintopt = envs->cintopt;
        const size_t Nbas = nbas;
        const int *ao_loc = envs->ao_loc;
        const int ish0 = images_loc[ishell];
        const int jsh0 = images_loc[jshell];
        const int ksh0 = images_loc[kshell];
        const int lsh0 = images_loc[lshell];
        const int jsh1 = images_loc[jshell+1];
        const int ksh1 = images_loc[kshell+1];
        const int lsh1 = images_loc[lshell+1];
        const int i0 = ao_loc[ishell];
        const int j0 = ao_loc[jshell];
        const int k0 = ao_loc[kshell];
        const int l0 = ao_loc[lshell];
        const int i1 = ao_loc[ishell+1];
        const int j1 = ao_loc[jshell+1];
        const int k1 = ao_loc[kshell+1];
        const int l1 = ao_loc[lshell+1];
        const int di = i1 - i0;
        const int dj = j1 - j0;
        const int dk = k1 - k0;
        const int dl = l1 - l0;
        const int dijkl = di * dj * dk * dl;
        double *q_cond_ijij = vhfopt->q_cond;
        double *q_cond_iijj = vhfopt->q_cond + Nbas*Nbas;
        double *q_cond_ij, *q_cond_kl, *q_cond_ik, *q_cond_jk;
        double *eri = eri_buf;
        double *bufL = eri_buf + dijkl;
        double *cache = bufL + dijkl;
        int shls[4] = {ish0};
        int n, jsh, ksh, lsh;
        double kl_cutoff, jl_cutoff, il_cutoff;

        int empty = 1;
        for (n = 0; n < dijkl; n++) {
                eri[n] = 0;
        }

        q_cond_ij = q_cond_ijij + ish0 * Nbas;
        q_cond_ik = q_cond_iijj + ish0 * Nbas;
        for (jsh = jsh0; jsh < jsh1; jsh++) {
                if (q_cond_ij[jsh] < cutoff) {
                        continue;
                }
                kl_cutoff = cutoff / q_cond_ij[jsh];
                q_cond_jk = q_cond_iijj + jsh * Nbas;
                for (ksh = ksh0; ksh < ksh1; ksh++) {
                        if (q_cond_ik[ksh] < cutoff ||
                            q_cond_jk[ksh] < cutoff) {
                                continue;
                        }
                        q_cond_kl = q_cond_ijij + ksh * Nbas;
                        jl_cutoff = cutoff / q_cond_ik[ksh];
                        il_cutoff = cutoff / q_cond_jk[ksh];
                        for (lsh = lsh0; lsh < lsh1; lsh++) {
                                if (q_cond_kl[lsh] < kl_cutoff ||
                                    q_cond_jk[lsh] < jl_cutoff ||
                                    q_cond_ik[lsh] < il_cutoff) {
                                        continue;
                                }
                                shls[1] = jsh;
                                shls[2] = ksh;
                                shls[3] = lsh;
                                if (int2e_sph(bufL, NULL, shls, atm, natm,
                                              bas, nbas, env, cintopt, cache)) {
                                        for (n = 0; n < dijkl; n++) {
                                                eri[n] += bufL[n];
                                        }
                                        empty = 0;
                                }
                        }
                }

        }
        return !empty;
}

void PBCVHF_contract_k_s1(double *vk, double *dms, double *buf,
                          int n_dm, int nkpts, int nbands, int nbasp,
                          int ish, int jsh, int ksh, int lsh,
                          int *bvk_cell_id, int *cell0_shl_id,
                          int *images_loc, int *dm_translation,
                          CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_jk_off = dm_translation[cell_j * nkpts + cell_k];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_jk_cond = vhfopt->dm_cond[dm_jk_off*nn0 + jshp*Nbasp+kshp];
        if (dm_jk_cond < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_jk_cond;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        int idm, i, jp, kp, lp, n;
        double sjk, qijkl;
        double *dm_jk;
        vk += cell_l * naop;

        for (idm = 0; idm < n_dm; idm++) {
                dm_jk = dms + dm_jk_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                for (jp = jp0; jp < jp1; jp++) {
                        sjk = dm_jk[jp*naop+kp];
                        for (i = i0; i < i1; i++, n++) {
                                qijkl = buf[n];
                                vk[i*bn+lp] += qijkl * sjk;
                        } } }
                }
                vk += bnn;
        }
}

static void contract_k_s2_kgtl(double *vk, double *dms, double *buf,
                          int n_dm, int nkpts, int nbands, int nbasp,
                          int ish, int jsh, int ksh, int lsh,
                          int *bvk_cell_id, int *cell0_shl_id,
                          int *images_loc, int *dm_translation,
                          CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_jk_off = dm_translation[cell_j*nkpts+cell_k];
        const int dm_jl_off = dm_translation[cell_j*nkpts+cell_l];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_jk_cond = vhfopt->dm_cond[dm_jk_off*nn0 + jshp*Nbasp+kshp];
        double dm_jl_cond = vhfopt->dm_cond[dm_jl_off*nn0 + jshp*Nbasp+lshp];
        double dm_cond_max = MAX(dm_jk_cond, dm_jl_cond);
        if (dm_cond_max < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_cond_max;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        int idm, i, jp, kp, lp, n;
        double sjk, sjl, qijkl;
        double *dm_jk, *dm_jl;
        double *vk_ik = vk + cell_k * naop;
        double *vk_il = vk + cell_l * naop;

        for (idm = 0; idm < n_dm; idm++) {
                dm_jk = dms + dm_jk_off * nn + idm * knn;
                dm_jl = dms + dm_jl_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                for (jp = jp0; jp < jp1; jp++) {
                        sjk = dm_jk[jp*naop+kp];
                        sjl = dm_jl[jp*naop+lp];
                        for (i = i0; i < i1; i++, n++) {
                                qijkl = buf[n];
                                vk_il[i*bn+lp] += qijkl * sjk;
                                vk_ik[i*bn+kp] += qijkl * sjl;
                        } } }
                }
                vk_ik += bnn;
                vk_il += bnn;
        }
}

void PBCVHF_contract_k_s2kl(double *vk, double *dms, double *buf,
                            int n_dm, int nkpts, int nbands, int nbasp,
                            int ish, int jsh, int ksh, int lsh,
                            int *bvk_cell_id, int *cell0_shl_id,
                            int *images_loc, int *dm_translation,
                            CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ksh > lsh) {
                contract_k_s2_kgtl(vk, dms, buf, n_dm, nkpts, nbands, nbasp,
                                   ish, jsh, ksh, lsh, bvk_cell_id,
                                   cell0_shl_id, images_loc,
                                   dm_translation, vhfopt, envs);
        } else if (ksh == lsh) {
                PBCVHF_contract_k_s1(vk, dms, buf, n_dm, nkpts, nbands, nbasp,
                                     ish, jsh, ksh, lsh, bvk_cell_id,
                                     cell0_shl_id, images_loc,
                                     dm_translation, vhfopt, envs);
        }
}

void PBCVHF_contract_j_s1(double *vj, double *dms, double *buf,
                          int n_dm, int nkpts, int nbands, int nbasp,
                          int ish, int jsh, int ksh, int lsh,
                          int *bvk_cell_id, int *cell0_shl_id,
                          int *images_loc, int *dm_translation,
                          CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_lk_off = dm_translation[cell_l * nkpts + cell_k];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_lk_cond = vhfopt->dm_cond[dm_lk_off*nn0 + lshp*Nbasp+kshp];
        if (dm_lk_cond < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_lk_cond;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        int idm, i, jp, kp, lp, n;
        double slk, qijkl;
        double *dm_lk;
        vj += cell_j * naop;

        for (idm = 0; idm < n_dm; idm++) {
                dm_lk = dms + dm_lk_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                        slk = dm_lk[lp*naop+kp];
                        for (jp = jp0; jp < jp1; jp++) {
                        for (i = i0; i < i1; i++, n++) {
                                qijkl = buf[n];
                                vj[i*bn+jp] += qijkl * slk;
                        } }
                } }
                vj += bnn;
        }
}

static void contract_j_s2_kgtl(double *vj, double *dms, double *buf,
                          int n_dm, int nkpts, int nbands, int nbasp,
                          int ish, int jsh, int ksh, int lsh,
                          int *bvk_cell_id, int *cell0_shl_id,
                          int *images_loc, int *dm_translation,
                          CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_lk_off = dm_translation[cell_l * nkpts + cell_k];
        const int dm_kl_off = dm_translation[cell_k * nkpts + cell_l];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_lk_cond = vhfopt->dm_cond[dm_lk_off*nn0 + lshp*Nbasp+kshp];
        double dm_kl_cond = vhfopt->dm_cond[dm_kl_off*nn0 + kshp*Nbasp+lshp];
        double dm_cond_max = dm_lk_cond + dm_kl_cond;
        if (dm_cond_max < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_cond_max;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        int idm, i, jp, kp, lp, n;
        double slk, qijkl;
        double *dm_lk, *dm_kl;
        vj += cell_j * naop;

        for (idm = 0; idm < n_dm; idm++) {
                dm_lk = dms + dm_lk_off * nn + idm * knn;
                dm_kl = dms + dm_kl_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                        slk = dm_lk[lp*naop+kp] + dm_kl[kp*naop+lp];
                        for (jp = jp0; jp < jp1; jp++) {
                        for (i = i0; i < i1; i++, n++) {
                                qijkl = buf[n];
                                vj[i*bn+jp] += qijkl * slk;
                        } }
                } }
                vj += bnn;
        }
}

void PBCVHF_contract_j_s2kl(double *vj, double *dms, double *buf,
                            int n_dm, int nkpts, int nbands, int nbasp,
                            int ish, int jsh, int ksh, int lsh,
                            int *bvk_cell_id, int *cell0_shl_id,
                            int *images_loc, int *dm_translation,
                            CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ksh > lsh) {
                contract_j_s2_kgtl(vj, dms, buf, n_dm, nkpts, nbands, nbasp,
                                   ish, jsh, ksh, lsh, bvk_cell_id,
                                   cell0_shl_id, images_loc,
                                   dm_translation, vhfopt, envs);
        } else if (ksh == lsh) {
                PBCVHF_contract_j_s1(vj, dms, buf, n_dm, nkpts, nbands, nbasp,
                                     ish, jsh, ksh, lsh, bvk_cell_id,
                                     cell0_shl_id, images_loc,
                                     dm_translation, vhfopt, envs);
        }
}

void PBCVHF_contract_jk_s1(double *jk, double *dms, double *buf,
                           int n_dm, int nkpts, int nbands, int nbasp,
                           int ish, int jsh, int ksh, int lsh,
                           int *bvk_cell_id, int *cell0_shl_id,
                           int *images_loc, int *dm_translation,
                           CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_lk_off = dm_translation[cell_l * nkpts + cell_k];
        const int dm_jk_off = dm_translation[cell_j * nkpts + cell_k];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_lk_cond = vhfopt->dm_cond[dm_lk_off*nn0 + lshp*Nbasp+kshp];
        double dm_jk_cond = vhfopt->dm_cond[dm_jk_off*nn0 + jshp*Nbasp+kshp];
        double dm_cond_max = MAX(dm_lk_cond, dm_jk_cond);
        if (dm_cond_max < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_cond_max;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        double *vj = jk + cell_j * naop;
        double *vk = jk + n_dm * bnn + cell_l * naop;
        int idm, i, jp, kp, lp, n;
        double slk, sjk, qijkl;
        double *dm_lk, *dm_jk;

        for (idm = 0; idm < n_dm; idm++) {
                dm_lk = dms + dm_lk_off * nn + idm * knn;
                dm_jk = dms + dm_jk_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                        slk = dm_lk[lp*naop+kp];
                        for (jp = jp0; jp < jp1; jp++) {
                                sjk = dm_jk[jp*naop+kp];
                                for (i = i0; i < i1; i++, n++) {
                                        qijkl = buf[n];
                                        vj[i*bn+jp] += qijkl * slk;
                                        vk[i*bn+lp] += qijkl * sjk;
                                }
                        }
                } }
                vj += bnn;
                vk += bnn;
        }
}

static void contract_jk_s2_kgtl(double *jk, double *dms, double *buf,
                                int n_dm, int nkpts, int nbands, int nbasp,
                                int ish, int jsh, int ksh, int lsh,
                                int *bvk_cell_id, int *cell0_shl_id,
                                int *images_loc, int *dm_translation,
                                CVHFOpt *vhfopt, IntorEnvs *envs)
{
        const int cell_j = bvk_cell_id[jsh];
        const int cell_k = bvk_cell_id[ksh];
        const int cell_l = bvk_cell_id[lsh];
        const int jshp = cell0_shl_id[jsh];
        const int kshp = cell0_shl_id[ksh];
        const int lshp = cell0_shl_id[lsh];
        const int dm_jk_off = dm_translation[cell_j*nkpts+cell_k];
        const int dm_jl_off = dm_translation[cell_j*nkpts+cell_l];
        const int dm_lk_off = dm_translation[cell_l*nkpts+cell_k];
        const int dm_kl_off = dm_translation[cell_k*nkpts+cell_l];
        const size_t Nbasp = nbasp;
        const size_t nn0 = Nbasp * Nbasp;
        double direct_scf_cutoff = vhfopt->direct_scf_cutoff;
        double dm_jk_cond = vhfopt->dm_cond[dm_jk_off*nn0 + jshp*Nbasp+kshp];
        double dm_jl_cond = vhfopt->dm_cond[dm_jl_off*nn0 + jshp*Nbasp+lshp];
        double dm_lk_cond = vhfopt->dm_cond[dm_lk_off*nn0 + lshp*Nbasp+kshp];
        double dm_kl_cond = vhfopt->dm_cond[dm_kl_off*nn0 + kshp*Nbasp+lshp];
        double dm_cond_max = MAX(dm_jk_cond, dm_jl_cond);
        dm_cond_max = MAX(dm_cond_max, dm_lk_cond + dm_kl_cond);
        if (dm_cond_max < direct_scf_cutoff) {
                return;
        } else {
                direct_scf_cutoff /= dm_cond_max;
        }
        if (!_assemble_eris(buf, images_loc, ish, jsh, ksh, lsh,
                            direct_scf_cutoff, vhfopt, envs)) {
                return;
        }

        const int *ao_loc = envs->ao_loc;
        const size_t naop = ao_loc[nbasp];
        const size_t nn = naop * naop;
        const size_t bn = naop * nbands;
        const size_t knn = nn * nkpts;
        const size_t bnn = bn * naop;
        const int i0  = ao_loc[ish];
        const int jp0 = ao_loc[jshp];
        const int kp0 = ao_loc[kshp];
        const int lp0 = ao_loc[lshp];
        const int i1  = ao_loc[ish+1];
        const int jp1 = ao_loc[jshp+1];
        const int kp1 = ao_loc[kshp+1];
        const int lp1 = ao_loc[lshp+1];
        double *vj = jk + cell_j * naop;
        double *vk_ik = jk + n_dm * bnn + cell_k * naop;
        double *vk_il = jk + n_dm * bnn + cell_l * naop;
        int idm, i, jp, kp, lp, n;
        double sjk, sjl, slk, qijkl;
        double *dm_jk, *dm_jl, *dm_lk, *dm_kl;

        for (idm = 0; idm < n_dm; idm++) {
                dm_lk = dms + dm_lk_off * nn + idm * knn;
                dm_kl = dms + dm_kl_off * nn + idm * knn;
                dm_jk = dms + dm_jk_off * nn + idm * knn;
                dm_jl = dms + dm_jl_off * nn + idm * knn;
                n = 0;
                for (lp = lp0; lp < lp1; lp++) {
                for (kp = kp0; kp < kp1; kp++) {
                        slk = dm_lk[lp*naop+kp] + dm_kl[kp*naop+lp];
                        for (jp = jp0; jp < jp1; jp++) {
                                sjk = dm_jk[jp*naop+kp];
                                sjl = dm_jl[jp*naop+lp];
                                for (i = i0; i < i1; i++, n++) {
                                        qijkl = buf[n];
                                        vj[i*bn+jp] += qijkl * slk;
                                        vk_il[i*bn+lp] += qijkl * sjk;
                                        vk_ik[i*bn+kp] += qijkl * sjl;
                                } }
                        }
                }
                vj += bnn;
                vk_ik += bnn;
                vk_il += bnn;
        }
}

void PBCVHF_contract_jk_s2kl(double *jk, double *dms, double *buf,
                             int n_dm, int nkpts, int nbands, int nbasp,
                             int ish, int jsh, int ksh, int lsh,
                             int *bvk_cell_id, int *cell0_shl_id,
                             int *images_loc, int *dm_translation,
                             CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ksh > lsh) {
                contract_jk_s2_kgtl(jk, dms, buf, n_dm, nkpts, nbands, nbasp,
                                   ish, jsh, ksh, lsh, bvk_cell_id,
                                   cell0_shl_id, images_loc,
                                   dm_translation, vhfopt, envs);
        } else if (ksh == lsh) {
                PBCVHF_contract_jk_s1(jk, dms, buf, n_dm, nkpts, nbands, nbasp,
                                      ish, jsh, ksh, lsh, bvk_cell_id,
                                      cell0_shl_id, images_loc,
                                      dm_translation, vhfopt, envs);
        }
}

/*
 * shls_slice refers to the shells of entire sup-mol.
 * bvk_ao_loc are ao_locs of bvk-cell basis appeared in supmol (some basis are removed)
 * nbasp is the number of basis in primitive cell
 * dm_translation utilizes the translation symmetry for density matrices (wrt the full bvk-cell)
 * DM[M,N] = DM[N-M] by mapping the 2D subscripts to 1D subscripts
 */
void PBCVHF_direct_drv(void (*fdot)(), double *out, double *dms,
                       int n_dm, int nkpts, int nbands, int nbasp,
                       char *ovlp_mask, int *bvk_cell_id,
                       int *cell0_shl_id, int *images_loc,
                       int *shls_slice, int *bvk_ao_loc,
                       int *dm_translation, CINTOpt *cintopt, CVHFOpt *vhfopt,
                       int *atm, int natm, int *bas, int nbas, double *env)
{
        IntorEnvs envs = {natm, nbas, atm, bas, env, shls_slice, bvk_ao_loc,
                NULL, cintopt, 1};

        const size_t ish0 = shls_slice[0];
        const size_t ish1 = shls_slice[1];
        const size_t jsh0 = shls_slice[2];
        const size_t jsh1 = shls_slice[3];
        const size_t ksh0 = shls_slice[4];
        const size_t ksh1 = shls_slice[5];
        const size_t lsh0 = shls_slice[6];
        const size_t lsh1 = shls_slice[7];
        const size_t nish = ish1 - ish0;
        const size_t njsh = jsh1 - jsh0;
        const size_t nksh = ksh1 - ksh0;
        const size_t nlsh = lsh1 - lsh0;
        const int di = GTOmax_shell_dim(bvk_ao_loc, shls_slice, 1);
        const int cache_size = _max_cache_size(int2e_sph, shls_slice, images_loc,
                                               atm, natm, bas, nbas, env);
        const size_t nij = nish * njsh;
        const size_t naop = bvk_ao_loc[nbasp];

#pragma omp parallel
{
        size_t ij, n;
        int i, j, k, l;
        size_t size = n_dm * naop * naop * nbands;
        if (fdot == &PBCVHF_contract_jk_s2kl || fdot == &PBCVHF_contract_jk_s1) {
                size *= 2;  // vj and vk
        }
        double *v_priv = calloc(size, sizeof(double));
        double *buf = malloc(sizeof(double) * (di*di*di*di*2 + cache_size));

#pragma omp for schedule(dynamic, 1)
        for (ij = 0; ij < nij; ij++) {
                i = ij / njsh;
                j = ij % njsh;
                if (!ovlp_mask[i*njsh+j]) {
                        continue;
                }

                for (k = 0; k < nksh; k++) {
                for (l = 0; l < nlsh; l++) {
                        if (!ovlp_mask[k*nlsh+l]) {
                                continue;
                        }
                        (*fdot)(v_priv, dms, buf, n_dm, nkpts, nbands, nbasp,
                                i, j, k, l, bvk_cell_id, cell0_shl_id, images_loc,
                                dm_translation, vhfopt, &envs);
                } }
        }
#pragma omp critical
        {
                for (n = 0; n < size; n++) {
                        out[n] += v_priv[n];
                }
        }
        free(buf);
        free(v_priv);
}
}

/************************************************/
void CVHFset_int2e_q_cond(int (*intor)(), CINTOpt *cintopt, double *q_cond,
                          int *ao_loc, int *atm, int natm,
                          int *bas, int nbas, double *env);

static int _int2e_swap_jk(double *buf, int *dims, int *shls,
                          int *atm, int natm, int *bas, int nbas, double *env,
                          CINTOpt *cintopt, double *cache)
{
        int shls_swap_jk[4] = {shls[0], shls[2], shls[1], shls[3]};
        return int2e_sph(buf, dims, shls_swap_jk, atm, natm, bas, nbas, env, cintopt, cache);
}

void PBCVHFsetnr_direct_scf(CVHFOpt *opt, int (*intor)(), CINTOpt *cintopt,
                            int *ao_loc, int *atm, int natm,
                            int *bas, int nbas, double *env)
{
        /* This memory is released in void CVHFdel_optimizer, Don't know
         * why valgrind raises memory leak here */
        if (opt->q_cond) {
                free(opt->q_cond);
        }
        // nbas in the input arguments may different to opt->nbas.
        // Use opt->nbas because it is used in the prescreen function
        nbas = opt->nbas;
        size_t Nbas = nbas;
        opt->q_cond = (double *)malloc(sizeof(double) * Nbas * Nbas * 2);
        double *qcond_ijij = opt->q_cond;
        double *qcond_iijj = qcond_ijij + Nbas * Nbas;
        CVHFset_int2e_q_cond(intor, cintopt, qcond_ijij, ao_loc,
                             atm, natm, bas, nbas, env);
        CVHFset_int2e_q_cond(_int2e_swap_jk, cintopt, qcond_iijj, ao_loc,
                             atm, natm, bas, nbas, env);
}

/*
 * for given ksh, lsh, loop all ish, jsh
 */
void CVHFdot_nrs1(int (*intor)(), JKOperator **jkop, JKArray **vjk,
                  double **dms, double *buf, double *cache, int n_dm,
                  int *ishls, int *jshls, int *kshls, int *lshls,
                  CVHFOpt *vhfopt, IntorEnvs *envs)
{
        DECLARE_ALL;

        for (ish = ish0; ish < ish1; ish++) {
        for (jsh = jsh0; jsh < jsh1; jsh++) {
        for (ksh = ksh0; ksh < ksh1; ksh++) {
        for (lsh = lsh0; lsh < lsh1; lsh++) {
                INTOR_AND_CONTRACT;
        } } } }
}

void CVHFdot_nrs2ij(int (*intor)(), JKOperator **jkop, JKArray **vjk,
                    double **dms, double *buf, double *cache, int n_dm,
                    int *ishls, int *jshls, int *kshls, int *lshls,
                    CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ishls[0] > jshls[0]) {
                return CVHFdot_nrs1(intor, jkop, vjk, dms, buf, cache, n_dm,
                                    ishls, jshls, kshls, lshls, vhfopt, envs);
        } else if (ishls[0] == jshls[0]) {

                DECLARE_ALL;

                for (ish = ish0; ish < ish1; ish++) {
                for (jsh = jsh0; jsh <= ish; jsh++) {
                for (ksh = ksh0; ksh < ksh1; ksh++) {
                for (lsh = lsh0; lsh < lsh1; lsh++) {
                        INTOR_AND_CONTRACT;
                } } } }
        }
}

void CVHFdot_nrs2kl(int (*intor)(), JKOperator **jkop, JKArray **vjk,
                    double **dms, double *buf, double *cache, int n_dm,
                    int *ishls, int *jshls, int *kshls, int *lshls,
                    CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (kshls[0] > lshls[0]) {
                return CVHFdot_nrs1(intor, jkop, vjk, dms, buf, cache, n_dm,
                                    ishls, jshls, kshls, lshls, vhfopt, envs);
        } else if (kshls[0] == lshls[0]) {
                assert(kshls[1] == lshls[1]);

                DECLARE_ALL;

                for (ish = ish0; ish < ish1; ish++) {
                for (jsh = jsh0; jsh < jsh1; jsh++) {
                for (ksh = ksh0; ksh < ksh1; ksh++) {
                for (lsh = lsh0; lsh <= ksh; lsh++) {
                        INTOR_AND_CONTRACT;
                } } } }
        }
}

void CVHFdot_nrs4(int (*intor)(), JKOperator **jkop, JKArray **vjk,
                  double **dms, double *buf, double *cache, int n_dm,
                  int *ishls, int *jshls, int *kshls, int *lshls,
                  CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ishls[0] > jshls[0]) {
                return CVHFdot_nrs2kl(intor, jkop, vjk, dms, buf, cache, n_dm,
                                      ishls, jshls, kshls, lshls, vhfopt, envs);
        } else if (ishls[1] <= jshls[0]) {
                return;
        } else if (kshls[0] > lshls[0]) {  // ishls == jshls
                return CVHFdot_nrs2ij(intor, jkop, vjk, dms, buf, cache, n_dm,
                                      ishls, jshls, kshls, lshls, vhfopt, envs);
        } else if (kshls[0] == lshls[0]) {  // ishls == jshls
                assert(kshls[1] == lshls[1]);

                DECLARE_ALL;

                for (ish = ish0; ish < ish1; ish++) {
                for (jsh = jsh0; jsh <= ish; jsh++) {
                for (ksh = ksh0; ksh < ksh1; ksh++) {
                for (lsh = lsh0; lsh <= ksh; lsh++) {
                        INTOR_AND_CONTRACT;
                } } } }
        }
}

void CVHFdot_nrs8(int (*intor)(), JKOperator **jkop, JKArray **vjk,
                  double **dms, double *buf, double *cache, int n_dm,
                  int *ishls, int *jshls, int *kshls, int *lshls,
                  CVHFOpt *vhfopt, IntorEnvs *envs)
{
        if (ishls[0] > kshls[0]) {
                return CVHFdot_nrs4(intor, jkop, vjk, dms, buf, cache, n_dm,
                                    ishls, jshls, kshls, lshls, vhfopt, envs);
        } else if (ishls[0] < kshls[0]) {
                return;
        } else if ((ishls[1] <= jshls[0]) || (kshls[1] <= lshls[0])) {
                assert(ishls[1] == kshls[1]);
                return;
        }
        // else i == k && i >= j && k >= l
        assert(ishls[1] == kshls[1]);

        DECLARE_ALL;

        for (ish = ish0; ish < ish1; ish++) {
        for (jsh = jsh0; jsh < MIN(jsh1, ish+1); jsh++) {
        for (ksh = ksh0; ksh <= ish; ksh++) {
        for (lsh = lsh0; lsh < MIN(lsh1, ksh+1); lsh++) {
/* when ksh==ish, (lsh<jsh) misses some integrals (eg k<i&&l>j).
 * These integrals are calculated in the next (ish,jsh) pair. To show
 * that, we just need to prove that every elements in shell^4 appeared
 * only once in fjk_s8.  */
                if ((ksh == ish) && (lsh > jsh)) {
                        break;
                }
                INTOR_AND_CONTRACT;
        } } } }
}

static JKArray *allocate_JKArray(JKOperator *op, int *shls_slice, int *ao_loc, int ncomp)
{
        JKArray *jkarray = malloc(sizeof(JKArray));
        int ibra = op->ibra_shl0;
        int iket = op->iket_shl0;
        int obra = op->obra_shl0;
        int oket = op->oket_shl0;
        int v_bra_sh0 = shls_slice[obra];
        int v_ket_sh0 = shls_slice[oket];
        int v_bra_sh1 = shls_slice[obra+1];
        int v_ket_sh1 = shls_slice[oket+1];
        jkarray->v_ket_nsh  = shls_slice[oket+1] - shls_slice[oket];
        jkarray->dm_dims[0] = ao_loc[shls_slice[ibra+1]] - ao_loc[shls_slice[ibra]];
        jkarray->dm_dims[1] = ao_loc[shls_slice[iket+1]] - ao_loc[shls_slice[iket]];
        int v_rows = ao_loc[v_bra_sh1] - ao_loc[v_bra_sh0];
        int v_cols = ao_loc[v_ket_sh1] - ao_loc[v_ket_sh0];
        jkarray->offset0_outptr = v_bra_sh0 * jkarray->v_ket_nsh + v_ket_sh0;
        int outptr_size =((shls_slice[obra+1] - shls_slice[obra]) *
                          (shls_slice[oket+1] - shls_slice[oket]));
        int *outptr = malloc(sizeof(int) * outptr_size);
        jkarray->outptr = outptr;
        int i;
        for (i = 0; i < outptr_size; i++) {
                outptr[i] = NOVALUE;
        }
        jkarray->stack_size = 0;
        int data_size = v_rows * v_cols * ncomp;
        jkarray->data = malloc(sizeof(double) * data_size);
        jkarray->ncomp = ncomp;
        return jkarray;
}

static void deallocate_JKArray(JKArray *jkarray)
{
        free(jkarray->outptr);
        free(jkarray->data);
        free(jkarray);
}

static double *allocate_and_reorder_dm(JKOperator *op, double *dm,
                                       int *shls_slice, int *ao_loc)
{
        int ibra = op->ibra_shl0;
        int iket = op->iket_shl0;
        int ish0 = shls_slice[ibra];
        int jsh0 = shls_slice[iket];
        int ish1 = shls_slice[ibra+1];
        int jsh1 = shls_slice[iket+1];
        int ioff = ao_loc[ish0];
        int joff = ao_loc[jsh0];
        int nrow = ao_loc[ish1] - ioff;
        int ncol = ao_loc[jsh1] - joff;
        double *out = malloc(sizeof(double) * nrow*ncol);
        int ish, jsh, i0, i1, j0, j1, i, j, ij;

        ij = 0;
        for (ish = ish0; ish < ish1; ish++) {
        for (jsh = jsh0; jsh < jsh1; jsh++) {
                i0 = ao_loc[ish  ] - ioff;
                i1 = ao_loc[ish+1] - ioff;
                j0 = ao_loc[jsh  ] - joff;
                j1 = ao_loc[jsh+1] - joff;
                for (i = i0; i < i1; i++) {
                for (j = j0; j < j1; j++, ij++) {
                        out[ij] = dm[i*ncol+j];
                } }
        } }
        return out;
}

static void zero_out_vjk(double *vjk, JKOperator *op,
                         int *shls_slice, int *ao_loc, int ncomp)
{
        int obra = op->obra_shl0;
        int oket = op->oket_shl0;
        int ish0 = shls_slice[obra];
        int jsh0 = shls_slice[oket];
        int ish1 = shls_slice[obra+1];
        int jsh1 = shls_slice[oket+1];
        int nbra = ao_loc[ish1] - ao_loc[ish0];
        int nket = ao_loc[jsh1] - ao_loc[jsh0];
        NPdset0(vjk, ((size_t)nbra) * nket * ncomp);
}

static void assemble_v(double *vjk, JKOperator *op, JKArray *jkarray,
                       int *shls_slice, int *ao_loc)
{
        int obra = op->obra_shl0;
        int oket = op->oket_shl0;
        int ish0 = shls_slice[obra];
        int jsh0 = shls_slice[oket];
        int ish1 = shls_slice[obra+1];
        int jsh1 = shls_slice[oket+1];
        int njsh = jsh1 - jsh0;
        size_t vrow = ao_loc[ish1] - ao_loc[ish0];
        size_t vcol = ao_loc[jsh1] - ao_loc[jsh0];
        int ncomp = jkarray->ncomp;
        int voffset = ao_loc[ish0] * vcol + ao_loc[jsh0];
        int i, j, ish, jsh;
        int di, dj, icomp;
        int optr;
        double *data, *pv;

        for (ish = ish0; ish < ish1; ish++) {
        for (jsh = jsh0; jsh < jsh1; jsh++) {
                optr = jkarray->outptr[ish*njsh+jsh-jkarray->offset0_outptr];
                if (optr != NOVALUE) {
                        di = ao_loc[ish+1] - ao_loc[ish];
                        dj = ao_loc[jsh+1] - ao_loc[jsh];
                        data = jkarray->data + optr;
                        pv = vjk + ao_loc[ish]*vcol+ao_loc[jsh] - voffset;
                        for (icomp = 0; icomp < ncomp; icomp++) {
                                for (i = 0; i < di; i++) {
                                for (j = 0; j < dj; j++) {
                                        pv[i*vcol+j] += data[i*dj+j];
                                } }
                                pv += vrow * vcol;
                                data += di * dj;
                        }
                }
        } }
}

// Divide shls into subblocks with roughly equal number of AOs in each block
int CVHFshls_block_partition(int *block_loc, int *shls_slice, int *ao_loc)
{
        int ish0 = shls_slice[0];
        int ish1 = shls_slice[1];
        int ao_loc_last = ao_loc[ish0];
        int count = 1;
        int ish;

        block_loc[0] = ish0;
        for (ish = ish0 + 1; ish < ish1; ish++) {
                if (ao_loc[ish] - ao_loc_last > AO_BLOCK_SIZE) {
                        block_loc[count] = ish;
                        count++;
                        ao_loc_last = ao_loc[ish];
                }
        }
        block_loc[count] = ish1;
        return count;
}



/*
 * drv loop over ij, generate eris of kl for given ij, call fjk to
 * calculate vj, vk.
 * 
 * n_dm is the number of dms for one [array(ij|kl)], it is also the size of dms and vjk
 * ncomp is the number of components that produced by intor
 * shls_slice = [ishstart, ishend, jshstart, jshend, kshstart, kshend, lshstart, lshend]
 *
 * ao_loc[i+1] = ao_loc[i] + CINTcgto_spheric(i, bas)  for i = 0..nbas
 *
 * Return [(ptr[ncomp,nao,nao] in C-contiguous) for ptr in vjk]
 */
void CVHFnr_direct_drv(int (*intor)(), void (*fdot)(), JKOperator **jkop,
                       double **dms, double **vjk, int n_dm, int ncomp,
                       int *shls_slice, int *ao_loc,
                       CINTOpt *cintopt, CVHFOpt *vhfopt,
                       int *atm, int natm, int *bas, int nbas, double *env)
{
        IntorEnvs envs = {natm, nbas, atm, bas, env, shls_slice, ao_loc, NULL,
                cintopt, ncomp};
        int idm;
        double *tile_dms[n_dm];
        for (idm = 0; idm < n_dm; idm++) {
                zero_out_vjk(vjk[idm], jkop[idm], shls_slice, ao_loc, ncomp);
                tile_dms[idm] = allocate_and_reorder_dm(jkop[idm], dms[idm],
                                                        shls_slice, ao_loc);
        }

        const size_t di = GTOmax_shell_dim(ao_loc, shls_slice, 4);
        const size_t cache_size = GTOmax_cache_size(intor, shls_slice, 4,
                                                    atm, natm, bas, nbas, env);
        const int ish0 = shls_slice[0];
        const int ish1 = shls_slice[1];
        const int jsh0 = shls_slice[2];
        const int jsh1 = shls_slice[3];
        const int ksh0 = shls_slice[4];
        const int ksh1 = shls_slice[5];
        const int lsh0 = shls_slice[6];
        const int lsh1 = shls_slice[7];
        const int nish = ish1 - ish0;
        const int njsh = jsh1 - jsh0;
        const int nksh = ksh1 - ksh0;
        const int nlsh = lsh1 - lsh0;
        int *block_iloc = malloc(sizeof(int) * (nish + njsh + nksh + nlsh + 4));
        int *block_jloc = block_iloc + nish + 1;
        int *block_kloc = block_jloc + njsh + 1;
        int *block_lloc = block_kloc + nksh + 1;
        const size_t nblock_i = CVHFshls_block_partition(block_iloc, shls_slice+0, ao_loc);
        const size_t nblock_j = CVHFshls_block_partition(block_jloc, shls_slice+2, ao_loc);
        const size_t nblock_k = CVHFshls_block_partition(block_kloc, shls_slice+4, ao_loc);
        const size_t nblock_l = CVHFshls_block_partition(block_lloc, shls_slice+6, ao_loc);
        const size_t nblock_kl = nblock_k * nblock_l;
        const size_t nblock_jkl = nblock_j * nblock_kl;

#pragma omp parallel
{
        size_t i, j, k, l, r, blk_id;
        JKArray *v_priv[n_dm];
        for (i = 0; i < n_dm; i++) {
                v_priv[i] = allocate_JKArray(jkop[i], shls_slice, ao_loc, ncomp);
        }
        double *buf = malloc(sizeof(double) * (di*di*di*di*ncomp + cache_size));
        double *cache = buf + di*di*di*di*ncomp;
#pragma omp for nowait schedule(dynamic, 1)
        for (blk_id = 0; blk_id < nblock_jkl; blk_id++) {
                r = blk_id;
                j = r / nblock_kl ; r = r % nblock_kl;
                k = r / nblock_l  ; r = r % nblock_l;
                l = r;
                for (i = 0; i < nblock_i; i++) {
                        (*fdot)(intor, jkop, v_priv, tile_dms, buf, cache, n_dm,
                                block_iloc+i, block_jloc+j, block_kloc+k, block_lloc+l,
                                vhfopt, &envs);
                }
        }
#pragma omp critical
        {
                for (i = 0; i < n_dm; i++) {
                        assemble_v(vjk[i], jkop[i], v_priv[i], shls_slice, ao_loc);
                        deallocate_JKArray(v_priv[i]);
                }
        }
        free(buf);
}
        for (idm = 0; idm < n_dm; idm++) {
                free(tile_dms[idm]);
        }
        free(block_iloc);
}

