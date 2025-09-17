/*      Compiler: ECL 24.5.10                                         */
/*      Date: 2025/9/17 01:23 (yyyy/mm/dd)                            */
/*      Machine: Darwin 23.6.0 arm64                                  */
/*      Source: /Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/pre-generated/src/algebra/SPLNODE.lsp */
#include <ecl/ecl-cmp.h>
#include "/Users/runner/sage-local/var/tmp/sage/build/fricas-1.3.12/src/_build/target/aarch64-apple-darwin23.6.0/algebra/SPLNODE.eclh"
/*      function definition for SPLNODE;rep                           */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2088_splnode_rep_(cl_object v1_n_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = v1_n_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;per                           */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2089_splnode_per_(cl_object v1_r_, cl_object v2_)
{
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 value0 = v1_r_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;empty;%;3                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2090_splnode_empty___3_(cl_object v1_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v2;
  v2 = (v1_)->vector.self.t[8];
  T1 = _ecl_car(v2);
  T2 = _ecl_cdr(v2);
  T0 = (cl_env_copy->function=T1)->cfun.entry(1, T2);
 }
 {
  cl_object v2;
  v2 = (v1_)->vector.self.t[9];
  T2 = _ecl_car(v2);
  T3 = _ecl_cdr(v2);
  T1 = (cl_env_copy->function=T2)->cfun.entry(1, T3);
 }
 T2 = cl_vector(3, T0, T1, ECL_NIL);
 value0 = L2089_splnode_per_(T2, v1_);
 return value0;
}
/*      function definition for SPLNODE;empty?;%B;4                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2091_splnode_empty___b_4_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[12];
  T0 = _ecl_car(v3);
  T1 = L2088_splnode_rep_(v1_n_, v2_);
  T2 = (T1)->vector.self.t[0];
  T3 = _ecl_cdr(v3);
  if (Null((cl_env_copy->function=T0)->cfun.entry(2, T2, T3))) { goto L1; }
 }
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[13];
  T0 = _ecl_car(v3);
  T1 = L2088_splnode_rep_(v1_n_, v2_);
  T2 = (T1)->vector.self.t[1];
  T3 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(2, T2, T3);
  return value0;
 }
L1:;
 value0 = ECL_NIL;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;value;%V;5                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2092_splnode_value__v_5_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v2_);
 value0 = (T0)->vector.self.t[0];
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;condition;%C;6                */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2093_splnode_condition__c_6_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v2_);
 value0 = (T0)->vector.self.t[1];
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;status;%B;7                   */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2094_splnode_status__b_7_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v2_);
 value0 = (T0)->vector.self.t[2];
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;construct;VCB%;8              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2095_splnode_construct_vcb__8_(cl_object v1_v_, cl_object v2_t_, cl_object v3_b_, cl_object v4_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = cl_vector(3, v1_v_, v2_t_, v3_b_);
 value0 = L2089_splnode_per_(T0, v4_);
 return value0;
}
/*      function definition for SPLNODE;construct;VC%;9               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2096_splnode_construct_vc__9_(cl_object v1_v_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[18];
  T0 = _ecl_car(v4);
  T1 = _ecl_cdr(v4);
  value0 = (cl_env_copy->function=T0)->cfun.entry(4, v1_v_, v2_t_, ECL_NIL, T1);
  return value0;
 }
}
/*      function definition for SPLNODE;construct;R%;10               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2097_splnode_construct_r__10_(cl_object v1_vt_, cl_object v2_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[19];
  T0 = _ecl_car(v3);
  T1 = ECL_CONS_CAR(v1_vt_);
  T2 = ECL_CONS_CDR(v1_vt_);
  T3 = _ecl_cdr(v3);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T1, T2, T3);
  return value0;
 }
}
/*      function definition for SPLNODE;construct;LL;11               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2098_splnode_construct_ll_11_(cl_object v1_lvt_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3;
  cl_object v4_vt_;
  cl_object v5;
  v3 = ECL_NIL;
  v4_vt_ = ECL_NIL;
  v5 = ECL_NIL;
  v5 = ECL_NIL;
  v4_vt_ = ECL_NIL;
  v3 = v1_lvt_;
L7:;
  if (ECL_ATOM(v3)) { goto L15; }
  v4_vt_ = _ecl_car(v3);
  goto L13;
L15:;
  goto L8;
L13:;
  {
   cl_object v6;
   v6 = (v2_)->vector.self.t[21];
   T1 = _ecl_car(v6);
   T2 = _ecl_cdr(v6);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, v4_vt_, T2);
  }
  v5 = CONS(T0,v5);
  goto L19;
L19:;
  v3 = _ecl_cdr(v3);
  goto L7;
L8:;
  value0 = cl_nreverse(v5);
  return value0;
 }
}
/*      function definition for SPLNODE;construct;VLL;12              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2099_splnode_construct_vll_12_(cl_object v1_v_, cl_object v2_lt_, cl_object v3_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  cl_object v5_t_;
  cl_object v6;
  v4 = ECL_NIL;
  v5_t_ = ECL_NIL;
  v6 = ECL_NIL;
  v6 = ECL_NIL;
  v5_t_ = ECL_NIL;
  v4 = v2_lt_;
L7:;
  if (ECL_ATOM(v4)) { goto L15; }
  v5_t_ = _ecl_car(v4);
  goto L13;
L15:;
  goto L8;
L13:;
  {
   cl_object v7;
   v7 = (v3_)->vector.self.t[19];
   T1 = _ecl_car(v7);
   T2 = _ecl_cdr(v7);
   T0 = (cl_env_copy->function=T1)->cfun.entry(3, v1_v_, v5_t_, T2);
  }
  v6 = CONS(T0,v6);
  goto L19;
L19:;
  v4 = _ecl_cdr(v4);
  goto L7;
L8:;
  value0 = cl_nreverse(v6);
  return value0;
 }
}
/*      function definition for SPLNODE;copy;2%;13                    */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2100_splnode_copy_2__13_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0, T1, T2;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = ecl_function_dispatch(cl_env_copy,VV[47])(1, ecl_make_fixnum(3)) /*  MAKE_VEC */;
 T1 = L2088_splnode_rep_(v1_n_, v2_);
 T2 = cl_replace(2, T0, T1);
 value0 = L2089_splnode_per_(T2, v2_);
 return value0;
}
/*      function definition for SPLNODE;setValue!;%V%;14              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2101_splnode_setvalue___v__14_(cl_object v1_n_, cl_object v2_v_, cl_object v3_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v3_);
 (T0)->vector.self.t[0]= v2_v_;
 value0 = v1_n_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;setCondition!;%C%;15          */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2102_splnode_setcondition___c__15_(cl_object v1_n_, cl_object v2_t_, cl_object v3_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v3_);
 (T0)->vector.self.t[1]= v2_t_;
 value0 = v1_n_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;setStatus!;%B%;16             */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2103_splnode_setstatus___b__16_(cl_object v1_n_, cl_object v2_b_, cl_object v3_)
{
 cl_object T0;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v3_);
 (T0)->vector.self.t[2]= v2_b_;
 value0 = v1_n_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;setEmpty!;2%;17               */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2104_splnode_setempty__2__17_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0, T1, T2, T3;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = L2088_splnode_rep_(v1_n_, v2_);
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[8];
  T2 = _ecl_car(v3);
  T3 = _ecl_cdr(v3);
  T1 = (cl_env_copy->function=T2)->cfun.entry(1, T3);
 }
 (T0)->vector.self.t[0]= T1;
 T0 = L2088_splnode_rep_(v1_n_, v2_);
 {
  cl_object v3;
  v3 = (v2_)->vector.self.t[9];
  T2 = _ecl_car(v3);
  T3 = _ecl_cdr(v3);
  T1 = (cl_env_copy->function=T2)->cfun.entry(1, T3);
 }
 (T0)->vector.self.t[1]= T1;
 value0 = v1_n_;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;infLex?;2%MMB;18              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2105_splnode_inflex__2_mmb_18_(cl_object v1_n1_, cl_object v2_n2_, cl_object v3_o1_, cl_object v4_o2_, cl_object v5_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 T0 = _ecl_car(v3_o1_);
 T1 = L2088_splnode_rep_(v1_n1_, v5_);
 T2 = (T1)->vector.self.t[0];
 T3 = L2088_splnode_rep_(v2_n2_, v5_);
 T4 = (T3)->vector.self.t[0];
 T5 = _ecl_cdr(v3_o1_);
 if (Null((cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5))) { goto L1; }
 value0 = ECL_T;
 cl_env_copy->nvalues = 1;
 return value0;
L1:;
 {
  cl_object v6;
  v6 = (v5_)->vector.self.t[32];
  T0 = _ecl_car(v6);
  T1 = L2088_splnode_rep_(v1_n1_, v5_);
  T2 = (T1)->vector.self.t[0];
  T3 = L2088_splnode_rep_(v2_n2_, v5_);
  T4 = (T3)->vector.self.t[0];
  T5 = _ecl_cdr(v6);
  if (Null((cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5))) { goto L4; }
 }
 T0 = _ecl_car(v4_o2_);
 T1 = L2088_splnode_rep_(v1_n1_, v5_);
 T2 = (T1)->vector.self.t[1];
 T3 = L2088_splnode_rep_(v2_n2_, v5_);
 T4 = (T3)->vector.self.t[1];
 T5 = _ecl_cdr(v4_o2_);
 value0 = (cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5);
 return value0;
L4:;
 value0 = ECL_NIL;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;subNode?;2%MB;19              */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2106_splnode_subnode__2_mb_19_(cl_object v1_n1_, cl_object v2_n2_, cl_object v3_o2_, cl_object v4_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v5;
  v5 = (v4_)->vector.self.t[32];
  T0 = _ecl_car(v5);
  T1 = L2088_splnode_rep_(v1_n1_, v4_);
  T2 = (T1)->vector.self.t[0];
  T3 = L2088_splnode_rep_(v2_n2_, v4_);
  T4 = (T3)->vector.self.t[0];
  T5 = _ecl_cdr(v5);
  if (Null((cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5))) { goto L1; }
 }
 T0 = _ecl_car(v3_o2_);
 T1 = L2088_splnode_rep_(v1_n1_, v4_);
 T2 = (T1)->vector.self.t[1];
 T3 = L2088_splnode_rep_(v2_n2_, v4_);
 T4 = (T3)->vector.self.t[1];
 T5 = _ecl_cdr(v3_o2_);
 value0 = (cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5);
 return value0;
L1:;
 value0 = ECL_NIL;
 cl_env_copy->nvalues = 1;
 return value0;
}
/*      function definition for SPLNODE;=;2%B;20                      */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2107_splnode___2_b_20_(cl_object v1_n1_, cl_object v2_n2_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[37];
  T0 = _ecl_car(v4);
  T1 = L2088_splnode_rep_(v1_n1_, v3_);
  T2 = (T1)->vector.self.t[0];
  T3 = L2088_splnode_rep_(v2_n2_, v3_);
  T4 = (T3)->vector.self.t[0];
  T5 = _ecl_cdr(v4);
  if (Null((cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5))) { goto L1; }
 }
 value0 = ECL_NIL;
 cl_env_copy->nvalues = 1;
 return value0;
L1:;
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[38];
  T0 = _ecl_car(v4);
  T1 = L2088_splnode_rep_(v1_n1_, v3_);
  T2 = (T1)->vector.self.t[1];
  T3 = L2088_splnode_rep_(v2_n2_, v3_);
  T4 = (T3)->vector.self.t[1];
  T5 = _ecl_cdr(v4);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5);
  return value0;
 }
}
/*      function definition for SPLNODE;~=;2%B;21                     */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2108_splnode____2_b_21_(cl_object v1_n1_, cl_object v2_n2_, cl_object v3_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[32];
  T0 = _ecl_car(v4);
  T1 = L2088_splnode_rep_(v1_n1_, v3_);
  T2 = (T1)->vector.self.t[0];
  T3 = L2088_splnode_rep_(v2_n2_, v3_);
  T4 = (T3)->vector.self.t[0];
  T5 = _ecl_cdr(v4);
  if (Null((cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5))) { goto L1; }
 }
 value0 = ECL_NIL;
 cl_env_copy->nvalues = 1;
 return value0;
L1:;
 {
  cl_object v4;
  v4 = (v3_)->vector.self.t[40];
  T0 = _ecl_car(v4);
  T1 = L2088_splnode_rep_(v1_n1_, v3_);
  T2 = (T1)->vector.self.t[1];
  T3 = L2088_splnode_rep_(v2_n2_, v3_);
  T4 = (T3)->vector.self.t[1];
  T5 = _ecl_cdr(v4);
  value0 = (cl_env_copy->function=T0)->cfun.entry(3, T2, T4, T5);
  return value0;
 }
}
/*      function definition for SPLNODE;coerce;%Of;22                 */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2109_splnode_coerce__of_22_(cl_object v1_n_, cl_object v2_)
{
 cl_object T0, T1, T2, T3, T4, T5;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_l_;
  cl_object v4_o3_;
  cl_object v5_o2_;
  cl_object v6_l2_;
  cl_object v7_o1_;
  cl_object v8_l1_;
  v3_l_ = ECL_NIL;
  v4_o3_ = ECL_NIL;
  v5_o2_ = ECL_NIL;
  v6_l2_ = ECL_NIL;
  v7_o1_ = ECL_NIL;
  v8_l1_ = ECL_NIL;
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[44];
   T1 = _ecl_car(v9);
   T2 = _ecl_cdr(v9);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, VV[23], T2);
  }
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[45];
   T2 = _ecl_car(v9);
   T3 = L2088_splnode_rep_(v1_n_, v2_);
   T4 = (T3)->vector.self.t[0];
   T5 = _ecl_cdr(v9);
   T1 = (cl_env_copy->function=T2)->cfun.entry(2, T4, T5);
  }
  v8_l1_ = cl_list(2, T0, T1);
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[46];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v7_o1_ = (cl_env_copy->function=T0)->cfun.entry(2, v8_l1_, T1);
  }
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[44];
   T1 = _ecl_car(v9);
   T2 = _ecl_cdr(v9);
   T0 = (cl_env_copy->function=T1)->cfun.entry(2, VV[24], T2);
  }
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[47];
   T2 = _ecl_car(v9);
   T3 = L2088_splnode_rep_(v1_n_, v2_);
   T4 = (T3)->vector.self.t[1];
   T5 = _ecl_cdr(v9);
   T1 = (cl_env_copy->function=T2)->cfun.entry(2, T4, T5);
  }
  v6_l2_ = cl_list(2, T0, T1);
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[46];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v5_o2_ = (cl_env_copy->function=T0)->cfun.entry(2, v6_l2_, T1);
  }
  T0 = L2088_splnode_rep_(v1_n_, v2_);
  if (Null((T0)->vector.self.t[2])) { goto L32; }
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[44];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v4_o3_ = (cl_env_copy->function=T0)->cfun.entry(2, VV[25], T1);
  }
  goto L31;
L32:;
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[44];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   v4_o3_ = (cl_env_copy->function=T0)->cfun.entry(2, VV[26], T1);
  }
L31:;
  v3_l_ = cl_list(3, v7_o1_, v5_o2_, v4_o3_);
  {
   cl_object v9;
   v9 = (v2_)->vector.self.t[48];
   T0 = _ecl_car(v9);
   T1 = _ecl_cdr(v9);
   value0 = (cl_env_copy->function=T0)->cfun.entry(2, v3_l_, T1);
   return value0;
  }
 }
}
/*      function definition for SplittingNode;                        */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2110_splittingnode__(cl_object v1__1_, cl_object v2__2_)
{
 cl_object T0, T1;
 cl_object env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object value0;
TTL:
 {
  cl_object v3_pv__;
  cl_object v4_;
  cl_object v5_dv__;
  cl_object v6dv_2;
  cl_object v7dv_1;
  v3_pv__ = ECL_NIL;
  v4_ = ECL_NIL;
  v5_dv__ = ECL_NIL;
  v6dv_2 = ECL_NIL;
  v7dv_1 = ECL_NIL;
  v7dv_1 = ecl_function_dispatch(cl_env_copy,VV[58])(1, v1__1_) /*  devaluate */;
  v6dv_2 = ecl_function_dispatch(cl_env_copy,VV[58])(1, v2__2_) /*  devaluate */;
  v5_dv__ = cl_list(3, VV[28], v7dv_1, v6dv_2);
  v4_ = ecl_function_dispatch(cl_env_copy,VV[59])(1, ecl_make_fixnum(50)) /*  GETREFV */;
  (v4_)->vector.self.t[0]= v5_dv__;
  v3_pv__ = ecl_function_dispatch(cl_env_copy,VV[60])(3, ecl_make_fixnum(0), ecl_make_fixnum(0), ECL_NIL) /*  buildPredVector */;
  (v4_)->vector.self.t[3]= v3_pv__;
  T0 = cl_list(2, v7dv_1, v6dv_2);
  T1 = CONS(ecl_make_fixnum(1),v4_);
  ecl_function_dispatch(cl_env_copy,VV[61])(4, ECL_SYM_VAL(cl_env_copy,VV[29]), VV[28], T0, T1) /*  haddProp */;
  ecl_function_dispatch(cl_env_copy,VV[62])(1, v4_) /*  stuffDomainSlots */;
  (v4_)->vector.self.t[6]= v1__1_;
  (v4_)->vector.self.t[7]= v2__2_;
  v3_pv__ = (v4_)->vector.self.t[3];
  value0 = v4_;
  cl_env_copy->nvalues = 1;
  return value0;
 }
}
/*      function definition for SplittingNode                         */
/*      optimize speed 3, debug 0, space 0, safety 0                  */
static cl_object L2111_splittingnode_(volatile cl_narg narg, ...)
{
 cl_object T0, T1;
 cl_object volatile env0 = ECL_NIL;
 const cl_env_ptr cl_env_copy = ecl_process_env();
 cl_object volatile value0;
 cl_object volatile v1;
 ecl_va_list args; ecl_va_start(args,narg,narg,0);
 v1 = cl_grab_rest_args(args);
 ecl_va_end(args);
 {
  volatile cl_object v2;
  v2 = ECL_NIL;
  T0 = ecl_function_dispatch(cl_env_copy,VV[64])(1, v1) /*  devaluateList */;
  T1 = ecl_gethash_safe(VV[28],ECL_SYM_VAL(cl_env_copy,VV[29]),ECL_NIL);
  v2 = ecl_function_dispatch(cl_env_copy,VV[65])(3, T0, T1, VV[30]) /*  lassocShiftWithFunction */;
  if (Null(v2)) { goto L3; }
  value0 = ecl_function_dispatch(cl_env_copy,VV[66])(1, v2) /*  CDRwithIncrement */;
  return value0;
L3:;
  {
   volatile bool unwinding = FALSE;
   cl_index v3=ECL_STACK_INDEX(cl_env_copy),v4;
   ecl_frame_ptr next_fr;
   ecl_frs_push(cl_env_copy,ECL_PROTECT_TAG);
   if (__ecl_frs_push_result) {
     unwinding = TRUE; next_fr=cl_env_copy->nlj_fr;
   } else {
   {
    cl_object v5;
    T0 = (VV[27]->symbol.gfdef);
    v5 = cl_apply(2, T0, v1);
    v2 = ECL_T;
    cl_env_copy->values[0] = v5;
    cl_env_copy->nvalues = 1;
   }
   }
   ecl_frs_pop(cl_env_copy);
   v4=ecl_stack_push_values(cl_env_copy);
   if ((v2)!=ECL_NIL) { goto L11; }
   cl_remhash(VV[28], ECL_SYM_VAL(cl_env_copy,VV[29]));
L11:;
   ecl_stack_pop_values(cl_env_copy,v4);
   if (unwinding) ecl_unwind(cl_env_copy,next_fr);
   ECL_STACK_SET_INDEX(cl_env_copy,v3);
   return cl_env_copy->values[0];
  }
 }
}